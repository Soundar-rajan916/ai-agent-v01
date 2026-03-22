"""
ATS Chain
LangChain implementation for ATS resume analysis
"""
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from src.agent.chat_model import get_chat_model


# ATS Analysis Prompt
ATS_ANALYSIS_PROMPT = """You are an expert ATS (Applicant Tracking System) analyzer and resume reviewer.

Your task is to analyze a candidate's resume against a job description and provide a detailed analysis in STRICT JSON format.

## Instructions:
1. Carefully review the resume and job description
2. Compare skills, experience, and qualifications
3. Calculate an ATS compatibility score (0-100)
4. Identify matched skills (skills present in both)
5. Identify missing skills (required but not present)
6. Provide actionable improvement suggestions

## Output Format:
You MUST return a valid JSON object with this exact structure:
{{
    "score": <number between 0-100>,
    "matched_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "improvements": ["suggestion1", "suggestion2", ...]
}}

## Resume:
{resume_text}

## Job Description:
{job_description}

## Analysis (respond ONLY with valid JSON):
"""


def get_ats_chain():
    """
    Create and return the ATS analysis chain.

    Returns:
        RunnableSequence: Configured chain for ATS analysis
    """
    # Get the chat model
    llm = get_chat_model()

    # Create prompt template
    prompt = PromptTemplate(
        template=ATS_ANALYSIS_PROMPT,
        input_variables=["resume_text", "job_description"]
    )

    # Use StrOutputParser to avoid .content issues
    output_parser = StrOutputParser()

    # Create the chain using modern LangChain syntax
    chain = RunnableSequence(
        prompt,
        llm,
        output_parser
    )

    return chain
