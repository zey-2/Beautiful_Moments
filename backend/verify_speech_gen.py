import asyncio
import os
import sys

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents import generate_speech, SpeechOutput

async def main():
    print("Testing generate_speech...")
    try:
        speech = await generate_speech(
            title="Test Story",
            person="Alice",
            emotion="Happy",
            notes="A story about graduation."
        )
        print("Result type:", type(speech))
        if isinstance(speech, SpeechOutput):
            print("Success! Returned SpeechOutput.")
            print(f"Emotion: {speech.emotion}")
            print(f"Transcript: {speech.transcript}")
        else:
            print("Failed! Did not return SpeechOutput.")
            print("Result:", speech)
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
