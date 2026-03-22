"""
Response Schemas for the API
"""
from pydantic import BaseModel
from typing import List, Optional, Union


class ATSData(BaseModel):
    """ATS analysis data structure"""
    score: int
    matched_skills: List[str]
    missing_skills: List[str]
    improvements: List[str]


class ChatResponse(BaseModel):
    """Response model for chat mode"""
    type: str = "chat"
    message: str


class ATSResponse(BaseModel):
    """Response model for ATS mode"""
    type: str = "ats"
    data: ATSData


class ErrorResponse(BaseModel):
    """Response model for errors"""
    type: str = "error"
    message: str
    details: Optional[str] = None


# Union type for all responses
ResponseType = Union[ChatResponse, ATSResponse, ErrorResponse]
