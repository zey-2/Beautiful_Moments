"""
Workflow Agents for orchestrating multi-step AI processes.

This module provides a framework for building sequential agent pipelines
that maintain state across steps, enabling more coherent multi-step processes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from google import genai
from google.genai import types
import logging

# Create logger for LlmAgent
logger = logging.getLogger("backend.workflow.LlmAgent")


class Agent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, output_key: Optional[str] = None):
        self.name = name
        self.output_key = output_key
    
    @abstractmethod
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's logic.
        
        Args:
            state: Shared state dictionary containing data from previous agents
            
        Returns:
            Updated state dictionary
        """
        pass


class LlmAgent(Agent):
    """
    Agent that uses an LLM to generate content.
    
    This agent can access previous outputs from the state and save its
    output to a specified key for downstream agents.
    """
    
    def __init__(
        self,
        name: str,
        client: genai.Client,
        model: str = "gemini-2.5-flash-lite",
        system_instruction: Optional[str] = None,
        prompt_template: Optional[str] = None,
        output_key: Optional[str] = None,
        output_model: Optional[Type[BaseModel]] = None,
        response_mime_type: str = "application/json",
        config_overrides: Optional[Dict[str, Any]] = None,
        tools: Optional[list] = None
    ):
        """
        Initialize an LLM agent.
        
        Args:
            name: Agent name for logging/debugging
            client: Gemini client instance
            model: Model identifier
            system_instruction: System instruction for the model
            prompt_template: Template string that can reference state keys with {key}
            output_key: Key to save output in state (if None, output is not saved)
            output_model: Pydantic model for structured output validation
            response_mime_type: MIME type for response
            config_overrides: Additional config parameters
            tools: List of tools (e.g., google_search) available to the agent
        """
        super().__init__(name, output_key)
        self.client = client
        self.model = model
        self.system_instruction = system_instruction
        self.prompt_template = prompt_template
        self.output_model = output_model
        self.response_mime_type = response_mime_type
        self.config_overrides = config_overrides or {}
        self.tools = tools
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the LLM agent."""
        # Build prompt from template and state
        if self.prompt_template:
            prompt = self.prompt_template.format(**state)
        else:
            prompt = state.get("prompt", "")
        
        # Prepare config
        config_params = {}
        
        # Note: response_mime_type and tools cannot be used together
        if not self.tools:
            config_params["response_mime_type"] = self.response_mime_type
        
        if self.system_instruction:
            config_params["system_instruction"] = self.system_instruction
        
        if self.output_model:
            config_params["response_json_schema"] = self.output_model.model_json_schema()
        
        if self.tools:
            config_params["tools"] = self.tools
        
        # Apply any overrides
        config_params.update(self.config_overrides)
        
        # Handle contents (text + images if present)
        contents = state.get("contents", prompt)
        
        # Log the LLM request
        logger.debug(f"Sending out request, model: {self.model}, agent: {self.name}")
        logger.debug(
            f"\nLLM Request:\n"
            f"-----------------------------------------------------------\n"
            f"System Instruction:\n{self.system_instruction or 'None'}\n"
            f"-----------------------------------------------------------\n"
            f"Contents:\n{self._format_contents(contents)}\n"
            f"-----------------------------------------------------------\n"
        )
        
        # Generate content
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(**config_params)
        )
        
        # Log the LLM response
        logger.debug(
            f"\nLLM Response:\n"
            f"-----------------------------------------------------------\n"
            f"Text:\n{response.text}\n"
            f"-----------------------------------------------------------\n"
        )
        
        # Parse output
        if self.output_model:
            # When tools are used, the response might not be pure JSON
            # Try to extract JSON from the response
            response_text = response.text.strip()
            
            # First, try to parse as-is
            try:
                output = self.output_model.model_validate_json(response_text)
            except Exception:
                # If that fails and tools were used, try to extract JSON from markdown code blocks
                if self.tools:
                    import re
                    import json
                    
                    # Try to find JSON in code blocks
                    # Handle optional json tag, and optional whitespace before/after content
                    json_match = re.search(r'```(?:json)?\s*(.*?)```', response_text, re.DOTALL)
                    if json_match:
                        response_text = json_match.group(1).strip()
                    else:
                        # Try to find JSON object in the text
                        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if json_match:
                            response_text = json_match.group(0)
                    
                    try:
                        output = self.output_model.model_validate_json(response_text)
                    except Exception as e:
                        logger.error(f"Failed to parse response as JSON: {e}")
                        logger.error(f"Response text: {response_text}")
                        raise
                else:
                    raise
        else:
            output = response.text
        
        # Save to state if output_key is specified
        if self.output_key:
            state[self.output_key] = output
        
        return state
    
    def _format_contents(self, contents) -> str:
        """Format contents for logging, handling text and images."""
        if isinstance(contents, str):
            return contents
        elif isinstance(contents, list):
            formatted = []
            for item in contents:
                if isinstance(item, str):
                    formatted.append(item)
                else:
                    # For images or other objects
                    formatted.append(f"<{type(item).__name__}>")
            return "\n".join(formatted)
        else:
            return str(contents)


class SequentialAgent(Agent):
    """
    Agent that runs multiple sub-agents in sequence.
    
    Each sub-agent receives the state from the previous agent and can
    modify it for the next agent in the pipeline.
    """
    
    def __init__(self, name: str, sub_agents: list[Agent]):
        """
        Initialize a sequential agent.
        
        Args:
            name: Agent name for logging/debugging
            sub_agents: List of agents to run in sequence
        """
        super().__init__(name)
        self.sub_agents = sub_agents
    
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all sub-agents in sequence."""
        for agent in self.sub_agents:
            state = await agent.run(state)
        return state
