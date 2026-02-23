"""
Multi-model support for Benjamin Graham Intelligent Investor Agent.
Supports Grok (xAI) and Gemini (Google) models.
"""

import os
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class ModelProvider(Enum):
    GROK = "grok"
    GEMINI = "gemini"


@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    provider: ModelProvider
    model_name: str
    display_name: str
    api_key_env: str
    base_url: Optional[str] = None


# Available models
AVAILABLE_MODELS = {
    "grok-3": ModelConfig(
        provider=ModelProvider.GROK,
        model_name="grok-3",
        display_name="Grok 3",
        api_key_env="XAI_API_KEY",
        base_url="https://api.x.ai/v1"
    ),
    "grok-3-mini": ModelConfig(
        provider=ModelProvider.GROK,
        model_name="grok-3-mini",
        display_name="Grok 3 Mini (Faster)",
        api_key_env="XAI_API_KEY",
        base_url="https://api.x.ai/v1"
    ),
    "grok-4-1-fast": ModelConfig(
        provider=ModelProvider.GROK,
        model_name="grok-4-1-fast-non-reasoning",
        display_name="Grok 4.1 Fast",
        api_key_env="XAI_API_KEY",
        base_url="https://api.x.ai/v1"
    ),
}


def get_model_choices() -> list[tuple[str, str]]:
    """Return list of (model_id, display_name) tuples for UI."""
    return [(k, v.display_name) for k, v in AVAILABLE_MODELS.items()]


def get_llm_response(
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    api_key: Optional[str] = None
) -> str:
    """
    Get a response from the specified LLM.
    
    Args:
        model_id: Key from AVAILABLE_MODELS
        system_prompt: System/context prompt
        user_prompt: User's prompt/question
        api_key: Optional API key (uses env var if not provided)
        
    Returns:
        Model's response text
    """
    if model_id not in AVAILABLE_MODELS:
        raise ValueError(f"Unknown model: {model_id}")
    
    config = AVAILABLE_MODELS[model_id]
    key = api_key or os.getenv(config.api_key_env)
    
    if not key:
        raise ValueError(f"API key not found. Set {config.api_key_env} environment variable.")
    
    if config.provider == ModelProvider.GROK:
        return _call_grok(config, key, system_prompt, user_prompt)
    elif config.provider == ModelProvider.GEMINI:
        return _call_gemini(config, key, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")


def _call_grok(config: ModelConfig, api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Call xAI's Grok API."""
    from openai import OpenAI
    
    client = OpenAI(
        api_key=api_key,
        base_url=config.base_url
    )
    
    try:
        response = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        # If model name is wrong, provide helpful error
        error_msg = str(e)
        if "model" in error_msg.lower() or "not found" in error_msg.lower():
            raise ValueError(
                f"Model '{config.model_name}' not found. "
                f"Please verify the correct model name in xAI API documentation. "
                f"Error: {error_msg}"
            )
        raise


def _call_gemini(config: ModelConfig, api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Call Google's Gemini API."""
    import google.generativeai as genai
    
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(
        model_name=config.model_name,
        system_instruction=system_prompt
    )
    
    response = model.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=2000,
        )
    )
    
    return response.text

