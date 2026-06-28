from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class QuizQuestionCreate(BaseModel):
    question_text: str
    options: List[str]
    correct_option_index: int
    explanation: Optional[str] = None

class QuizQuestionResponse(QuizQuestionCreate):
    id: UUID
    quiz_id: UUID
    user_answer_index: Optional[int] = None
    created_at: datetime

class QuizCreate(BaseModel):
    title: str
    topic: str
    difficulty: str
    total_questions: int

class QuizResponse(QuizCreate):
    id: UUID
    user_id: UUID
    score: Optional[int] = None
    created_at: datetime
    questions: Optional[List[QuizQuestionResponse]] = None

class GenerateQuizRequest(BaseModel):
    topic: str
    difficulty: str = Field(default="medium")
    count: int = Field(default=5, ge=1, le=20)

class SubmitQuizRequest(BaseModel):
    answers: dict[str, int] # Mapping of question_id (str) to user_answer_index (int)
