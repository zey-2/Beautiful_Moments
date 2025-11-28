from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid
from ..database import get_db
from ..models import Story, Photo, StoryRead
from ..agents import generate_speech, generate_album_layout, generate_speech_audio

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

@router.post("/", response_model=StoryRead)
async def create_story(
    title: str = Form(...),
    person: str = Form(...),
    emotion: str = Form(...),
    notes: str = Form(...),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # 1. Save Story Metadata
    new_story = Story(
        title=title,
        person=person,
        emotion=emotion,
        notes=notes
    )
    db.add(new_story)
    db.commit()
    db.refresh(new_story)

    # 2. Save Photos
    saved_photo_paths = []
    if files:
        for file in files:
            # Generate unique filename
            ext = file.filename.split(".")[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(MEDIA_DIR, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            photo = Photo(story_id=new_story.id, file_path=file_path)
            db.add(photo)
            saved_photo_paths.append(file_path)
        db.commit()

    # 3. Run Agents
    # Speech
    # Speech
    speech_output = await generate_speech(title, person, emotion, notes)
    new_story.generated_speech = speech_output.transcript
    new_story.generated_voice_direction = speech_output.emotion
    
    # Generate audio from speech
    audio_path = await generate_speech_audio(speech_output.transcript, voice_direction=speech_output.emotion)
    new_story.audio_file_path = audio_path

    # Album
    album_json = await generate_album_layout(title, person, emotion, notes, saved_photo_paths)
    new_story.album_json = album_json

    db.commit()
    db.refresh(new_story)

    return new_story

@router.get("/", response_model=List[StoryRead])
def read_stories(db: Session = Depends(get_db)):
    stories = db.query(Story).all()
    return stories

@router.get("/{story_id}", response_model=StoryRead)
def read_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.put("/{story_id}", response_model=StoryRead)
def update_story(story_id: int, story_update: dict, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    for key, value in story_update.items():
        if hasattr(story, key):
            setattr(story, key, value)
    
    db.commit()
    db.refresh(story)
    return story

@router.post("/{story_id}/mark_used")
def mark_story_used(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    story.used_in_presentation = True
    db.commit()
    return {"status": "success"}

@router.delete("/{story_id}")
def delete_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Delete associated photos from filesystem
    photos = db.query(Photo).filter(Photo.story_id == story_id).all()
    for photo in photos:
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)
            print(f"Deleted photo file: {photo.file_path}")
    
    # Delete audio file from filesystem
    if story.audio_file_path and os.path.exists(story.audio_file_path):
        os.remove(story.audio_file_path)
        print(f"Deleted audio file: {story.audio_file_path}")
    
    # Delete story (cascade will delete photos from DB)
    db.delete(story)
    db.commit()
    return {"status": "deleted", "id": story_id}

@router.post("/reset")
def reset_stories(db: Session = Depends(get_db)):
    stories = db.query(Story).all()
    for story in stories:
        story.used_in_presentation = False
    db.commit()
    return {"status": "reset complete"}


@router.post("/{story_id}/photos")
async def add_photos_to_story(
    story_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")

    saved_photos = []
    for file in files:
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(MEDIA_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        photo = Photo(story_id=story_id, file_path=file_path)
        db.add(photo)
        saved_photos.append(photo)

    db.commit()

    for photo in saved_photos:
        db.refresh(photo)

    return {"status": "success", "photos": [
        {"id": p.id, "story_id": p.story_id, "file_path": p.file_path} for p in saved_photos
    ]}


@router.delete("/photos/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    if os.path.exists(photo.file_path):
        os.remove(photo.file_path)

    db.delete(photo)
    db.commit()

    return {"status": "deleted", "id": photo_id}


@router.post("/{story_id}/regenerate_transcript")
async def regenerate_transcript(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Regenerate transcript using the story's metadata
    speech_output = await generate_speech(story.title, story.person, story.emotion, story.notes)
    story.generated_speech = speech_output.transcript
    story.generated_voice_direction = speech_output.emotion
    
    db.commit()
    db.refresh(story)
    
    return {
        "status": "success",
        "generated_speech": speech_output.transcript,
        "generated_voice_direction": speech_output.emotion
    }

@router.post("/{story_id}/regenerate_audio")
async def regenerate_audio(story_id: int, speech_text: str = Form(None), db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if story is None:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Use provided speech_text or fall back to story's generated_speech
    text_to_use = speech_text if speech_text else story.generated_speech
    
    if not text_to_use:
        raise HTTPException(status_code=400, detail="No speech text available")
    
    # Delete old audio file if it exists
    if story.audio_file_path and os.path.exists(story.audio_file_path):
        os.remove(story.audio_file_path)
        print(f"Deleted old audio file: {story.audio_file_path}")
    
    # Generate new audio from speech text
    audio_path = await generate_speech_audio(text_to_use, voice_direction=story.generated_voice_direction)
    story.audio_file_path = audio_path
    
    db.commit()
    db.refresh(story)
    
    return {"status": "success", "audio_file_path": audio_path}
