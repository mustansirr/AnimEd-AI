import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from datetime import datetime

from app.models.quiz import (
    QuizResponse,
    GenerateQuizRequest,
    SubmitQuizRequest,
    QuizQuestionResponse,
    QuizCreate,
    QuizQuestionCreate
)
from app.services.supabase_client import get_supabase_client
from app.services.llm_factory import create_llm
from app.api.routes.videos import validate_uuid

router = APIRouter(prefix="/quizzes", tags=["quizzes"])

@router.get("", response_model=List[QuizResponse])
async def list_quizzes(user_id: str = Query(..., description="UUID of the user")):
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    result = (
        client.table("quizzes")
        .select("*")
        .eq("user_id", str(user_uuid))
        .order("created_at", desc=True)
        .execute()
    )
    return result.data

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: str, user_id: str = Query(..., description="UUID of the user")):
    quiz_uuid = validate_uuid(quiz_id, "quiz_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    # Get quiz
    quiz_res = client.table("quizzes").select("*").eq("id", str(quiz_uuid)).eq("user_id", str(user_uuid)).execute()
    if not quiz_res.data:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    quiz = quiz_res.data[0]
    
    # Get questions
    questions_res = client.table("quiz_questions").select("*").eq("quiz_id", str(quiz_uuid)).order("created_at", desc=False).execute()
    
    quiz["questions"] = questions_res.data
    return quiz

@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    req: GenerateQuizRequest,
    user_id: str = Query(..., description="UUID of the user")
):
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    llm = create_llm(role="planner", temperature=0.7)
    
    difficulty_instruction = ""
    if req.difficulty.lower() == "easy":
        difficulty_instruction = "The difficulty is easy. Ask basic questions suitable for a beginner."
    elif req.difficulty.lower() == "hard":
        difficulty_instruction = "The difficulty is hard. Ask advanced, complex questions suitable for an expert."
    else:
        difficulty_instruction = "The difficulty is medium. Ask moderately challenging questions suitable for a professional."

    prompt = f"""
You are an expert educator. Create a {req.count}-question multiple choice quiz on the following topic: '{req.topic}'.
{difficulty_instruction}
Return the output EXACTLY as a JSON array of objects.
Each object must have the following keys:
- 'question_text': string
- 'options': array of 4 string options
- 'correct_option_index': integer (0-3) representing the index of the correct option
- 'explanation': string explaining why the correct answer is correct

Do not include markdown formatting like ```json ... ```, just output the raw JSON array.
"""
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content="You generate valid JSON arrays of quiz questions."),
            HumanMessage(content=prompt)
        ]
        resp = llm.invoke(messages)
        content = resp.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        questions_data = json.loads(content)
        
        if not questions_data or len(questions_data) == 0:
            raise ValueError("No questions generated")
            
        # Create Quiz
        title = f"{req.topic} Quiz"
        quiz_res = client.table("quizzes").insert({
            "user_id": str(user_uuid),
            "title": title,
            "topic": req.topic,
            "difficulty": req.difficulty,
            "total_questions": len(questions_data)
        }).execute()
        
        if not quiz_res.data:
            raise HTTPException(status_code=500, detail="Failed to create quiz in DB")
            
        quiz = quiz_res.data[0]
        quiz_uuid = quiz["id"]
        
        # Create Questions
        created_questions = []
        for q in questions_data:
            insert_res = client.table("quiz_questions").insert({
                "quiz_id": str(quiz_uuid),
                "question_text": q["question_text"],
                "options": q["options"],
                "correct_option_index": q["correct_option_index"],
                "explanation": q.get("explanation", "")
            }).execute()
            if insert_res.data:
                created_questions.append(insert_res.data[0])
                
        quiz["questions"] = created_questions
        return quiz

    except Exception as e:
        import logging
        logging.error(f"Failed to generate quiz: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/{quiz_id}/submit", response_model=QuizResponse)
async def submit_quiz(
    quiz_id: str,
    req: SubmitQuizRequest,
    user_id: str = Query(..., description="UUID of the user")
):
    quiz_uuid = validate_uuid(quiz_id, "quiz_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    # Get questions
    questions_res = client.table("quiz_questions").select("*").eq("quiz_id", str(quiz_uuid)).execute()
    if not questions_res.data:
        raise HTTPException(status_code=404, detail="Quiz questions not found")
        
    questions = questions_res.data
    score = 0
    
    for q in questions:
        question_id = str(q["id"])
        if question_id in req.answers:
            user_answer = req.answers[question_id]
            is_correct = user_answer == q["correct_option_index"]
            if is_correct:
                score += 1
                
            # Update user's answer
            client.table("quiz_questions").update({"user_answer_index": user_answer}).eq("id", question_id).execute()
            
    # Update quiz score
    updated_quiz_res = client.table("quizzes").update({"score": score}).eq("id", str(quiz_uuid)).eq("user_id", str(user_uuid)).execute()
    if not updated_quiz_res.data:
        raise HTTPException(status_code=500, detail="Failed to update quiz score")
        
    quiz = updated_quiz_res.data[0]
    
    # Fetch updated questions
    updated_questions_res = client.table("quiz_questions").select("*").eq("quiz_id", str(quiz_uuid)).order("created_at", desc=False).execute()
    quiz["questions"] = updated_questions_res.data
    
    return quiz

@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: str,
    user_id: str = Query(..., description="UUID of the user")
):
    quiz_uuid = validate_uuid(quiz_id, "quiz_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    client.table("quizzes").delete().eq("id", str(quiz_uuid)).eq("user_id", str(user_uuid)).execute()
    return None

@router.post("/{quiz_id}/retake", response_model=QuizResponse)
async def retake_quiz(
    quiz_id: str,
    user_id: str = Query(..., description="UUID of the user")
):
    quiz_uuid = validate_uuid(quiz_id, "quiz_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    # Check if quiz exists and belongs to user
    quiz_res = client.table("quizzes").select("*").eq("id", str(quiz_uuid)).eq("user_id", str(user_uuid)).execute()
    if not quiz_res.data:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    # Reset quiz score
    updated_quiz_res = client.table("quizzes").update({"score": None}).eq("id", str(quiz_uuid)).eq("user_id", str(user_uuid)).execute()
    if not updated_quiz_res.data:
        raise HTTPException(status_code=500, detail="Failed to reset quiz score")
        
    quiz = updated_quiz_res.data[0]
    
    # Reset all questions' user_answer_index
    client.table("quiz_questions").update({"user_answer_index": None}).eq("quiz_id", str(quiz_uuid)).execute()
    
    # Fetch reset questions
    updated_questions_res = client.table("quiz_questions").select("*").eq("quiz_id", str(quiz_uuid)).order("created_at", desc=False).execute()
    quiz["questions"] = updated_questions_res.data
    
    return quiz
