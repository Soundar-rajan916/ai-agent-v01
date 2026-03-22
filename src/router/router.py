"""
Router Logic
Handles the main routing logic for chat vs ATS mode
"""
from typing import Tuple, Optional
from src.tools.pdf_tool import extract_text_from_pdf
from src.tools.jd_tool import generate_job_description
from src.tools.ats_tool import perform_ats_analysis


def is_job_title(message: str) -> bool:
    """
    Determine if the message is a job title rather than a full job description.

    Heuristics:
    - Short length (under 100 characters)
    - No newlines
    - Looks like a title (contains common job words or is brief)

    Args:
        message: User's message

    Returns:
        bool: True if likely a job title, False if likely a JD
    """
    message = message.strip()

    # If it's too long, it's probably a JD
    if len(message) > 300:
        return False

    # If it has multiple paragraphs, it's probably a JD
    if '\n\n' in message or message.count('\n') > 3:
        return False

    # If it has bullet points, it's probably a JD
    if '-' in message and message.count('-') > 2:
        return False

    # Common job description keywords that indicate full JD
    jd_indicators = [
        "responsibilities", "requirements", "qualifications",
        "experience required", "skills needed", "job summary",
        "position overview", "what you'll do", "we are looking for",
        "must have", "preferred", "education", "benefits"
    ]

    message_lower = message.lower()
    for indicator in jd_indicators:
        if indicator in message_lower:
            return False

    return True


def detect_message_type(message: str) -> str:
    """
    Detect the type of message provided by the user.

    Args:
        message: User's message

    Returns:
        str: "job_title" or "job_description"
    """
    if is_job_title(message):
        return "job_title"
    return "job_description"


def process_resume_request(
    message: str,
    resume_text: Optional[str] = None
) -> Tuple[str, Optional[dict]]:
    """
    Process a resume-related request.

    Cases:
    A. Resume + Job Description → ATS analysis
    B. Resume + Job Title → Generate JD → ATS analysis
    C. Resume only → Ask for JD

    Args:
        message: User's message (JD or job title)
        resume_text: Extracted resume text (if file uploaded)

    Returns:
        Tuple of (response_type, data)
        response_type: "ats", "error", or "request_jd"
        data: ATS data or error message
    """
    # Case C: Resume only, no message
    if not message or not message.strip():
        return "request_jd", None

    # Detect if message is job title or full JD
    message_type = detect_message_type(message)

    job_description = message

    # Case B: Generate JD if it's just a job title
    if message_type == "job_title":
        job_description = generate_job_description(message)

    # Case A & B: Perform ATS analysis
    if resume_text:
        ats_result = perform_ats_analysis(resume_text, job_description)
        return "ats", ats_result

    return "request_jd", None


def generate_chat_response(message: str) -> str:
    """
    Generate a normal chat response for non-resume queries.

    Args:
        message: User's message

    Returns:
        str: AI response
    """
    from src.agent.chat_model import get_chat_model
    from langchain_core.messages import HumanMessage

    try:
        llm = get_chat_model()
        response = llm.invoke([HumanMessage(content=message)])
        return response.content
    except Exception as e:
        return f"I apologize, but I'm having trouble processing your request. Error: {str(e)}"
