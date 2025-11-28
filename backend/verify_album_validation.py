"""
Test script to verify album layout generation only uses valid photo IDs.
"""

import asyncio
import os
import sys
import json

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents import generate_album_layout


async def main():
    print("=" * 60)
    print("Testing Album Layout Generation - Photo ID Validation")
    print("=" * 60)
    print()
    
    # Test with a small number of images
    test_image_paths = [
        "media/test1.jpg",  # These don't need to exist for this test
        "media/test2.jpg",
        "media/test3.jpg"
    ]
    
    print(f"Testing with {len(test_image_paths)} images")
    print(f"Valid photo_id range: 0 to {len(test_image_paths) - 1}")
    print()
    
    try:
        layout_json = await generate_album_layout(
            title="Champion",
            person="Boon King",
            emotion="Joyful",
            notes="The class comedian, always brings laughter and livens up the room.",
            image_paths=test_image_paths
        )
        
        print("Generated Layout:")
        print("-" * 60)
        
        # Parse and pretty print
        layout = json.loads(layout_json)
        print(json.dumps(layout, indent=2))
        print()
        
        # Validate photo IDs
        print("=" * 60)
        print("Validation Results:")
        print("=" * 60)
        
        if "photos" in layout:
            photo_ids = [p.get("photo_id") for p in layout["photos"]]
            print(f"Photo IDs in layout: {photo_ids}")
            print(f"Number of photos: {len(photo_ids)}")
            
            invalid_ids = [pid for pid in photo_ids if pid >= len(test_image_paths)]
            if invalid_ids:
                print(f"❌ FAILED: Found invalid photo IDs: {invalid_ids}")
                print(f"   (Valid range is 0-{len(test_image_paths)-1})")
            else:
                print(f"✅ SUCCESS: All photo IDs are valid (0-{len(test_image_paths)-1})")
        else:
            print("⚠️  No photos array found in layout")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
