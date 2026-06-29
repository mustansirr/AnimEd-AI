from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class FlashcardDeckBase(BaseModel):
    title: str
    description: Optional[str] = None

class FlashcardDeckCreate(FlashcardDeckBase):
    pass

class FlashcardDeckResponse(FlashcardDeckBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FlashcardBase(BaseModel):
    front: str
    back: str

class FlashcardCreate(FlashcardBase):
    pass

class FlashcardResponse(FlashcardBase):
    id: UUID
    deck_id: UUID
    user_id: UUID
    next_review_date: datetime
    interval: int
    ease_factor: float
    repetitions: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FlashcardReview(BaseModel):
    # Rating scale: 1 = Again, 2 = Hard, 3 = Good, 4 = Easy
    rating: int = Field(..., ge=1, le=4)

class GenerateFlashcardsRequest(BaseModel):
    topic: str
    count: int = Field(default=5, ge=1, le=20)
