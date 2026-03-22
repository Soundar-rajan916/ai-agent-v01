"""
Chat Model Configuration
Uses Groq with gpt-oss-120b model
"""
from langchain_groq import ChatGroq
from langchain_core.language_models import BaseChatModel
import os
from dotenv import load_dotenv

load_dotenv()

def get_chat_model() -> BaseChatModel:
    """
    Initialize and return the Groq chat model.
    Uses gpt-oss-120b model via Groq API.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=api_key,
        temperature=0.2,
        max_tokens=4096,
    )
