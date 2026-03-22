"""
Main FastAPI Application
AI Chat Agent with ATS Resume Analysis
"""
import sys
import os

# Add parent directory to path for imports - go up to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Chat Agent with ATS",
    description="An AI chat system with ATS resume analysis capabilities",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "AI Chat Agent with ATS API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat - Main chat endpoint with optional file upload",
            "health": "GET /health - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-chat-ats"}


@app.post("/chat")
async def chat(
    message: str = Form(..., description="User message (job description or job title)"),
    file: Optional[UploadFile] = File(None, description="Optional PDF resume file")
):
    """
    Main chat endpoint.

    - If no file: Behaves like a normal AI chat assistant
    - If file uploaded:
      - If message is long text → Treat as Job Description → ATS analysis
      - If message is short (job title) → Generate JD → ATS analysis
      - If no message → Ask for JD

    Args:
        message: User's message (form field)
        file: Optional PDF resume file

    Returns:
        JSON response with type "chat" or "ats"
    """
    try:
        # Import here to avoid circular imports
        from src.tools.pdf_tool import extract_text_from_pdf
        from src.router.router import process_resume_request, generate_chat_response

        logger.info(f"Received chat request with message length: {len(message)}")
        if file:
            logger.info(f"File uploaded: {file.filename}")

        # Case: File uploaded → ATS Mode
        if file:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF files are supported"
                )

            # Extract text from PDF
            try:
                resume_text = await extract_text_from_pdf(file)
                logger.info(f"Extracted {len(resume_text)} characters from PDF")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"PDF extraction error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to extract text from PDF: {str(e)}"
                )

            # Process the request
            response_type, data = process_resume_request(message, resume_text)

            if response_type == "request_jd":
                return JSONResponse(
                    status_code=200,
                    content={
                        "type": "chat",
                        "message": "Please provide a job description or job role for ATS analysis."
                    }
                )

            elif response_type == "ats":
                return JSONResponse(
                    status_code=200,
                    content={
                        "type": "ats",
                        "data": data
                    }
                )

            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "type": "error",
                        "message": "An error occurred during processing",
                        "details": data if data else "Unknown error"
                    }
                )

        # Case: No file → Normal Chat Mode
        else:
            response_text = generate_chat_response(message)
            return JSONResponse(
                status_code=200,
                content={
                    "type": "chat",
                    "message": response_text
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "error",
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "type": "error",
            "message": "Internal server error",
            "details": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
