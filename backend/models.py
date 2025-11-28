from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# SQLAlchemy Models

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    person = Column(String)
    emotion = Column(String)

    notes = Column(Text)
    generated_speech = Column(Text, nullable=True)
    generated_voice_direction = Column(Text, nullable=True)
    album_json = Column(Text, nullable=True)
    audio_file_path = Column(String, nullable=True)
    used_in_presentation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    photos = relationship("Photo", back_populates="story")

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"))
    file_path = Column(String)

    story = relationship("Story", back_populates="photos")

# Pydantic Schemas

class PhotoBase(BaseModel):
    file_path: str

class PhotoRead(PhotoBase):
    id: int
    story_id: int

    class Config:
        from_attributes = True

class StoryBase(BaseModel):
    title: str
    person: str
    emotion: str

    notes: str

class StoryCreate(StoryBase):
    pass

class StoryRead(StoryBase):
    id: int
    generated_speech: Optional[str] = None
    generated_voice_direction: Optional[str] = None
    album_json: Optional[str] = None
    audio_file_path: Optional[str] = None
    used_in_presentation: bool
    created_at: datetime
    photos: List[PhotoRead] = []

    class Config:
        from_attributes = True
