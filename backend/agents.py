import os
import uuid
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pathlib import Path
import json
import PIL.Image
import io
from typing import Dict, Any

from .workflow import LlmAgent, SequentialAgent

# Load .env from the backend directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables")

SPEECH_SYSTEM_INSTRUCTION = """
You are a speech and emotional-direction generator for a valedictorian speech.

Your goal:
- Craft a short, powerful passage that captures the emotional centre of the valedictorian's message.
- Length: around 100 words (80–120 words).
- Style: spoken, natural, vivid, and suitable for AI voice performance.
- You have access to Google Search to find current information, news, or facts if needed.

Output requirements:
- You must return JSON with exactly two fields that match the schema:
  - "emotion": A single line of voice direction in parentheses, starting with "Voice:".
    Example: "(Voice: Warm, enthusiastic, filled with genuine delight)"
  - "transcript": The full speech passage.
- The transcript:
  - Should be thematically unified around the user's story.
  - May include light performance cues in brackets, e.g. "(slight chuckle)", "(pause)".
  - Should not explain what you are doing or mention JSON, fields, or schemas.

Stay focused on emotional clarity and performance-ready language.
"""

class SpeechOutput(BaseModel):
    # Example: "(Voice: Warm, enthusiastic, filled with genuine delight)"
    emotion: str = Field(
        description=(
            "A single parenthesised voice direction line, starting with 'Voice:'. "
            "Example: '(Voice: Warm, enthusiastic, filled with genuine delight)'."
        )
    )
    # The actual spoken text
    transcript: str = Field(
        description=(
            "The speech transcript, around 80–120 words, written as if spoken aloud."
        )
    )

ALBUM_SYSTEM_INSTRUCTION = """
You are an album layout designer. Your task is to create a structured JSON layout for a graduation album page based on the provided story metadata and images.

CRITICAL CONSTRAINTS:
- Typically, 1-4 images will be provided per story.
- You will be told EXACTLY how many images are provided (e.g., "3 images provided").
- You MUST ONLY create photo entries for the images that were actually provided.
- photo_id values MUST be 0-based indices (0, 1, 2, ...) and MUST NOT exceed the number of images provided.
- If 3 images are provided, you can ONLY use photo_id values: 0, 1, 2
- If 4 images are provided, you can ONLY use photo_id values: 0, 1, 2, 3
- DO NOT create entries for images that don't exist.

Output STRICT JSON with:
- `page_title`
- `page_description`
- `photos`: array containing ONLY entries for the provided images:
    - `photo_id`: 0-based index of the actual image (must be < number of images provided)
    - `role`: `main`, `side`, or `background`
    - `caption`: max 20 words
"""

async def generate_speech(title: str, person: str, emotion: str, notes: str) -> SpeechOutput:
    if not client:
        return SpeechOutput(
            emotion="(Voice: Neutral, mock generated)",
            transcript="Gemini API Key not found. Mock speech generated."
        )
    
    # Create the speech generation agent
    speech_agent = LlmAgent(
        name="SpeechGenerator",
        client=client,
        model='gemini-2.5-flash-lite',
        system_instruction=SPEECH_SYSTEM_INSTRUCTION,
        prompt_template="""
Title: {title}
Person: {person}
Emotion: {emotion}
Notes: {notes}

Generate the speech passage. You MUST respond with valid JSON matching the schema with "emotion" and "transcript" fields.

Example Output:
```json
{{
  "emotion": "(Voice: Warm and reflective)",
  "transcript": "As we stand here today..."
}}
```
""",
        output_key="speech",
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
    
    # Initialize state with input parameters
    state: Dict[str, Any] = {
        "title": title,
        "person": person,
        "emotion": emotion,
        "notes": notes
    }
    
    try:
        # Run the agent
        result_state = await speech_agent.run(state)
        response_text = result_state["speech"]
        
        # Try to parse as JSON
        try:
            # Check for code blocks first
            import re
            json_match = re.search(r'```(?:json)?\s*(.*?)```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1).strip()
            else:
                json_text = response_text
            
            data = json.loads(json_text)
            return SpeechOutput(**data)
        except Exception:
            # Fallback: Parse text format "(Voice: ...)\nTranscript..."
            voice_match = re.search(r'^\s*\(Voice:\s*(.*?)\)', response_text, re.DOTALL | re.IGNORECASE)
            if voice_match:
                emotion = f"(Voice: {voice_match.group(1)})"
                # Transcript is everything after the voice direction
                transcript = response_text[voice_match.end():].strip()
                return SpeechOutput(emotion=emotion, transcript=transcript)
            
            # If all else fails, return as transcript with default emotion
            return SpeechOutput(
                emotion="(Voice: Neutral)",
                transcript=response_text
            )

    except Exception as e:
        print(f"Error generating speech: {repr(e)}")
        return SpeechOutput(
            emotion="(Voice: Error)",
            transcript="Error generating speech."
        )

import wave

def save_wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Save PCM data to a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

async def generate_speech_audio(speech_text: str, voice_direction: str = None) -> str:
    """Generate audio file from speech text using GenAI SDK with Gemini 2.5 Flash TTS."""
    if not client:
        return ""
    
    try:
        # Use Gemini 2.5 Flash TTS with audio response modality
        # Construct prompt with voice direction if available
        prompt_text = f"Read the following text clearly: '{speech_text}'"
        if voice_direction:
            prompt_text = f"{voice_direction} Read the following text: '{speech_text}'"

        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-tts',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Despina"
                        )
                    )
                )
            )
        )
        
        # Get audio bytes from the response
        if hasattr(response, 'candidates') and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    audio_bytes = part.inline_data.data
                    
                    # Generate unique filename
                    filename = f"{uuid.uuid4()}.wav"
                    file_path = os.path.join(MEDIA_DIR, filename)
                    
                    # Save audio file using wave module
                    save_wave_file(file_path, audio_bytes)
                    
                    return file_path
        
        print("No audio data found in response")
        return ""
    except Exception as e:
        print(f"Error generating speech audio: {e}")
        return ""

async def generate_album_layout(title: str, person: str, emotion: str, notes: str, image_paths: list[str]) -> str:
    if not client:
        return json.dumps({
            "page_title": title,
            "page_description": "Mock description due to missing API key.",
            "photos": []
        })

    # Create the album layout agent
    album_agent = LlmAgent(
        name="AlbumLayoutGenerator",
        client=client,
        model='gemini-2.5-flash-lite',
        system_instruction=ALBUM_SYSTEM_INSTRUCTION,
        output_key="album_layout"
    )
    
    # Prepare text prompt with explicit image count
    num_images = len(image_paths)
    text_prompt = f"""Title: {title}
Person: {person}
Emotion: {emotion}
Notes: {notes}

IMAGES PROVIDED: {num_images} images (photo_id range: 0 to {num_images - 1})

Generate the album layout JSON using ONLY the {num_images} images provided."""
    
    # Build contents list with text and images
    contents = [text_prompt]
    for path in image_paths:
        try:
            img = PIL.Image.open(path)
            contents.append(img)
        except Exception as e:
            print(f"Could not load image {path}: {e}")
    
    # Initialize state
    state: Dict[str, Any] = {
        "contents": contents
    }

    try:
        # Run the agent
        result_state = await album_agent.run(state)
        layout_json = result_state["album_layout"]
        
        # Post-process: Validate and filter photo IDs
        try:
            layout_data = json.loads(layout_json)
            if "photos" in layout_data:
                valid_photos = []
                for photo in layout_data["photos"]:
                    photo_id = photo.get("photo_id")
                    if isinstance(photo_id, int) and 0 <= photo_id < num_images:
                        valid_photos.append(photo)
                    else:
                        print(f"Warning: Filtered out invalid photo_id {photo_id} (valid range: 0-{num_images-1})")
                
                layout_data["photos"] = valid_photos
                return json.dumps(layout_data)
        except json.JSONDecodeError:
            # If we can't parse it, return as-is
            pass
        
        return layout_json
    except Exception as e:
        print(f"Error generating album layout: {e}")
        return json.dumps({"error": "Failed to generate layout"})
