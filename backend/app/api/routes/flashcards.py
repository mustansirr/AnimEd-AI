import json
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.models.flashcard import (
    FlashcardDeckCreate,
    FlashcardDeckResponse,
    FlashcardCreate,
    FlashcardResponse,
    FlashcardReview,
    GenerateFlashcardsRequest
)
from app.services.supabase_client import get_supabase_client
from app.services.llm_factory import create_llm
from app.api.routes.videos import validate_uuid

router = APIRouter(prefix="/flashcards", tags=["flashcards"])

# =============================================================================
# Decks
# =============================================================================

@router.get("/decks", response_model=List[FlashcardDeckResponse])
async def list_decks(user_id: str = Query(..., description="UUID of the user")):
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    result = (
        client.table("flashcard_decks")
        .select("*")
        .eq("user_id", str(user_uuid))
        .order("created_at", desc=True)
        .execute()
    )
    return result.data

@router.post("/decks", response_model=FlashcardDeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck: FlashcardDeckCreate,
    user_id: str = Query(..., description="UUID of the user")
):
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    result = (
        client.table("flashcard_decks")
        .insert({
            "user_id": str(user_uuid),
            "title": deck.title,
            "description": deck.description
        })
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create deck")
    return result.data[0]

@router.put("/decks/{deck_id}", response_model=FlashcardDeckResponse)
async def update_deck(
    deck_id: str,
    deck: FlashcardDeckCreate,
    user_id: str = Query(..., description="UUID of the user")
):
    deck_uuid = validate_uuid(deck_id, "deck_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    result = (
        client.table("flashcard_decks")
        .update({
            "title": deck.title,
            "description": deck.description
        })
        .eq("id", str(deck_uuid))
        .eq("user_id", str(user_uuid))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Deck not found or update failed")
    return result.data[0]

@router.delete("/decks/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: str,
    user_id: str = Query(..., description="UUID of the user")
):
    deck_uuid = validate_uuid(deck_id, "deck_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    result = (
        client.table("flashcard_decks")
        .delete()
        .eq("id", str(deck_uuid))
        .eq("user_id", str(user_uuid))
        .execute()
    )
    # The Supabase Python client might return an empty list in .data if delete was successful 
    # but didn't return representation, or it might return the deleted row.
    return None

# =============================================================================
# Flashcards
# =============================================================================

@router.get("/decks/{deck_id}/cards", response_model=List[FlashcardResponse])
async def list_cards_in_deck(deck_id: str):
    deck_uuid = validate_uuid(deck_id, "deck_id")
    client = get_supabase_client()
    
    result = (
        client.table("flashcards")
        .select("*")
        .eq("deck_id", str(deck_uuid))
        .order("created_at", desc=False)
        .execute()
    )
    return result.data

@router.post("/decks/{deck_id}/cards", response_model=FlashcardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    deck_id: str,
    card: FlashcardCreate,
    user_id: str = Query(..., description="UUID of the user")
):
    deck_uuid = validate_uuid(deck_id, "deck_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    # Ensure deck exists and belongs to user
    deck_res = client.table("flashcard_decks").select("id").eq("id", str(deck_uuid)).eq("user_id", str(user_uuid)).execute()
    if not deck_res.data:
        raise HTTPException(status_code=404, detail="Deck not found")
        
    result = (
        client.table("flashcards")
        .insert({
            "deck_id": str(deck_uuid),
            "user_id": str(user_uuid),
            "front": card.front,
            "back": card.back
        })
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create card")
    return result.data[0]


@router.put("/{card_id}/review", response_model=FlashcardResponse)
async def review_card(card_id: str, review: FlashcardReview):
    card_uuid = validate_uuid(card_id, "card_id")
    client = get_supabase_client()
    
    res = client.table("flashcards").select("*").eq("id", str(card_uuid)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Card not found")
        
    card = res.data[0]
    
    # SM-2 Algorithm Simplified
    rating = review.rating # 1: Again, 2: Hard, 3: Good, 4: Easy
    
    ease_factor = card["ease_factor"]
    repetitions = card["repetitions"]
    interval = card["interval"]
    
    if rating == 1: # Again
        repetitions = 0
        interval = 1
        ease_factor = max(1.3, ease_factor - 0.2)
    elif rating == 2: # Hard
        interval = max(1, int(interval * 1.2))
        ease_factor = max(1.3, ease_factor - 0.15)
    elif rating == 3: # Good
        repetitions += 1
        interval = 1 if repetitions == 1 else 6 if repetitions == 2 else int(interval * ease_factor)
    elif rating == 4: # Easy
        repetitions += 1
        interval = 1 if repetitions == 1 else 6 if repetitions == 2 else int(interval * ease_factor * 1.3)
        ease_factor += 0.15
        
    from datetime import datetime, timedelta
    next_review_date = datetime.utcnow() + timedelta(days=interval)
    
    update_res = (
        client.table("flashcards")
        .update({
            "next_review_date": next_review_date.isoformat(),
            "interval": interval,
            "ease_factor": ease_factor,
            "repetitions": repetitions
        })
        .eq("id", str(card_uuid))
        .execute()
    )
    
    if not update_res.data:
        raise HTTPException(status_code=500, detail="Failed to update card")
    return update_res.data[0]

# =============================================================================
# AI Generation
# =============================================================================

@router.post("/decks/{deck_id}/generate", response_model=List[FlashcardResponse])
async def generate_cards(
    deck_id: str,
    req: GenerateFlashcardsRequest,
    user_id: str = Query(..., description="UUID of the user")
):
    deck_uuid = validate_uuid(deck_id, "deck_id")
    user_uuid = validate_uuid(user_id, "user_id")
    client = get_supabase_client()
    
    # Ensure deck exists
    deck_res = client.table("flashcard_decks").select("id").eq("id", str(deck_uuid)).eq("user_id", str(user_uuid)).execute()
    if not deck_res.data:
        raise HTTPException(status_code=404, detail="Deck not found")
        
    llm = create_llm(role="planner", temperature=0.7)
    
    prompt = f"""
You are an expert educator. Create {req.count} flashcards based on the following topic.
Return the output EXACTLY as a JSON array of objects, with each object having a 'front' (the question/concept) and a 'back' (the answer/explanation). Do not include markdown formatting like ```json ... ```, just output the raw JSON array.

Topic:
{req.topic}
"""
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content="You generate valid JSON arrays of flashcards."),
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
        
        cards_data = json.loads(content)
        
        created_cards = []
        for c in cards_data:
            insert_res = client.table("flashcards").insert({
                "deck_id": str(deck_uuid),
                "user_id": str(user_uuid),
                "front": c["front"],
                "back": c["back"]
            }).execute()
            if insert_res.data:
                created_cards.append(insert_res.data[0])
                
        return created_cards

    except Exception as e:
        import logging
        logging.error(f"Failed to generate flashcards: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
