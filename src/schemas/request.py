"""
Request Schemas for the API
"""
from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Tell me about resume writing tips"
            }
        }


class ATSRequest(BaseModel):
    """Request model for ATS analysis"""
    message: str
    resume_text: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Software Engineer position",
                "resume_text": "Experienced Python developer..."
            }
        }
