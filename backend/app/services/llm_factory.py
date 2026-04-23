"""
LLM Factory — Configurable per-agent LLM instantiation.

Creates LLM instances based on environment-variable settings.
Each agent role (planner, scripter, coder, reflector) can be
independently configured to use a different provider and model.

Lookup order for each role:
  1. Role-specific env vars  (e.g. CODER_LLM_PROVIDER, CODER_LLM_MODEL)
  2. Global defaults         (LLM_PROVIDER, LLM_MODEL)
"""

import logging
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel

from app.config import get_settings

logger = logging.getLogger(__name__)

# Type alias for supported roles
AgentRole = Literal["planner", "scripter", "coder", "reflector"]


def create_llm(role: AgentRole, temperature: float = 0.7) -> BaseChatModel:
    """
    Create an LLM instance for the given agent role.

    Resolves provider and model from role-specific settings first,
    then falls back to global defaults.

    Args:
        role: The agent role ("planner", "scripter", "coder", "reflector").
        temperature: Sampling temperature for the LLM.

    Returns:
        A configured BaseChatModel instance (ChatGroq or ChatOpenRouter).

    Raises:
        ValueError: If the resolved provider is not supported or
                    the required API key is missing.
    """
    settings = get_settings()

    # Resolve provider: role-specific → global
    role_provider = getattr(settings, f"{role}_llm_provider", None)
    provider = role_provider or settings.llm_provider

    # Resolve model: role-specific → global
    role_model = getattr(settings, f"{role}_llm_model", None)
    model = role_model or settings.llm_model

    logger.info(
        f"[{role}] Creating LLM — provider={provider}, model={model}, "
        f"temperature={temperature}"
    )

    if provider == "groq":
        return _create_groq_llm(model, temperature, settings.groq_api_key)
    elif provider == "openrouter":
        return _create_openrouter_llm(
            model, temperature, settings.openrouter_api_key
        )
    else:
        raise ValueError(
            f"Unsupported LLM provider '{provider}' for role '{role}'. "
            f"Supported: groq, openrouter"
        )


def _create_groq_llm(
    model: str, temperature: float, api_key: str
) -> BaseChatModel:
    """Create a ChatGroq instance."""
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is required when using the 'groq' provider. "
            "Set it in your .env file."
        )

    from langchain_groq import ChatGroq

    return ChatGroq(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )


def _create_openrouter_llm(
    model: str, temperature: float, api_key: str
) -> BaseChatModel:
    """Create a ChatOpenRouter instance."""
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is required when using the 'openrouter' "
            "provider. Set it in your .env file."
        )

    from langchain_openrouter import ChatOpenRouter

    return ChatOpenRouter(
        model=model,
        temperature=temperature,
        api_key=api_key,
    )
