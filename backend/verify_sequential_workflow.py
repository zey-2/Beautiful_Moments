"""
Example demonstrating SequentialAgent for multi-step workflow orchestration.

This script shows how to use SequentialAgent to create a pipeline where
each agent's output feeds into the next agent's input, maintaining coherency
across the entire process.
"""

import asyncio
import os
import sys

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents import client, SPEECH_SYSTEM_INSTRUCTION, SpeechOutput
from backend.workflow import LlmAgent, SequentialAgent
from pydantic import BaseModel, Field
from typing import Dict, Any


class StoryTheme(BaseModel):
    """Theme analysis for a story."""
    theme: str = Field(description="The central theme of the story")
    key_emotions: list[str] = Field(description="List of 2-3 key emotions")
    suggested_tone: str = Field(description="Suggested tone for the speech")


async def main():
    if not client:
        print("ERROR: GEMINI_API_KEY not found. Cannot run example.")
        return
    
    print("=" * 60)
    print("Sequential Agent Example: Multi-Step Story Processing")
    print("=" * 60)
    print()
    
    # Step 1: Analyze the story theme
    theme_analyzer = LlmAgent(
        name="ThemeAnalyzer",
        client=client,
        model='gemini-2.5-flash-lite',
        system_instruction="You are a literary analyst. Extract the theme and emotional core from story notes.",
        prompt_template="""
Analyze this story:
Title: {title}
Person: {person}
Notes: {notes}

Identify the theme, key emotions, and suggested tone.
""",
        output_key="theme_analysis",
        output_model=StoryTheme
    )
    
    # Step 2: Generate speech using the theme analysis
    speech_generator = LlmAgent(
        name="SpeechGenerator",
        client=client,
        model='gemini-2.5-flash-lite',
        system_instruction=SPEECH_SYSTEM_INSTRUCTION,
        prompt_template="""
Title: {title}
Person: {person}
Theme: {theme_analysis.theme}
Key Emotions: {theme_analysis.key_emotions}
Suggested Tone: {theme_analysis.suggested_tone}
Notes: {notes}

Generate the speech passage incorporating the identified theme and emotions.
""",
        output_key="speech",
        output_model=SpeechOutput
    )
    
    # Create a sequential pipeline
    pipeline = SequentialAgent(
        name="StoryToSpeechPipeline",
        sub_agents=[theme_analyzer, speech_generator]
    )
    
    # Initialize state with input data
    state: Dict[str, Any] = {
        "title": "The Journey Ahead",
        "person": "Sarah Chen",
        "notes": "A story about overcoming challenges together as a class, celebrating diversity, and looking forward to the future with hope and determination."
    }
    
    print("Input State:")
    print(f"  Title: {state['title']}")
    print(f"  Person: {state['person']}")
    print(f"  Notes: {state['notes']}")
    print()
    
    # Run the pipeline
    print("Running Sequential Pipeline...")
    print()
    
    result_state = await pipeline.run(state)
    
    # Display results
    print("=" * 60)
    print("STEP 1: Theme Analysis")
    print("=" * 60)
    theme: StoryTheme = result_state["theme_analysis"]
    print(f"Theme: {theme.theme}")
    print(f"Key Emotions: {', '.join(theme.key_emotions)}")
    print(f"Suggested Tone: {theme.suggested_tone}")
    print()
    
    print("=" * 60)
    print("STEP 2: Generated Speech")
    print("=" * 60)
    speech: SpeechOutput = result_state["speech"]
    print(f"Emotion: {speech.emotion}")
    print()
    print(f"Transcript:\n{speech.transcript}")
    print()
    
    print("=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
