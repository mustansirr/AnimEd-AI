"""
Context Retrieval Node.

This node fetches relevant syllabus context using the RAG service
at the beginning of the workflow.
"""

from uuid import UUID

from app.agents.state import AgentState
from app.services.rag_service import retrieve_context


async def retrieve_context_node(state: AgentState) -> dict:
    """
    Retrieve syllabus context using RAG service.

    This is the entry point node that enriches the state with
    relevant context from any uploaded PDF syllabus.

    Args:
        state: Current agent state.

    Returns:
        Updated state dict with syllabus_context populated.
    """
    video_id = state["video_id"]
    user_prompt = state["user_prompt"]

    # Skip if context already provided
    if state.get("syllabus_context"):
        return {}

    try:
        # Retrieve context from RAG service
        context = await retrieve_context(
            query=user_prompt,
            video_id=UUID(video_id),
            top_k=5,
            threshold=0.5
        )
        return {"syllabus_context": context}

    except Exception:
        # If RAG fails, continue without context
        return {"syllabus_context": ""}
