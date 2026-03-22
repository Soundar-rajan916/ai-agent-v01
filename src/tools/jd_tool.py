"""
Job Description Generator Tool
Generates detailed job description from a job title
"""
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from src.agent.chat_model import get_chat_model


# Prompt for generating job descriptions
JD_GENERATION_PROMPT = """You are an expert HR professional and job description writer.

Given a job title, create a comprehensive and detailed job description that includes:
1. Job Summary (2-3 sentences)
2. Key Responsibilities (5-7 bullet points)
3. Required Skills (technical and soft skills)
4. Qualifications (education, certifications, experience)
5. Preferred Skills (nice to have)

Job Title: {job_title}

Generate a detailed job description below:
"""


def generate_job_description(job_title: str) -> str:
    """
    Generate a detailed job description from a job title.

    Args:
        job_title: The job title (e.g., "AI Engineer", "Software Developer")

    Returns:
        str: Detailed job description
    """
    try:
        # Get the chat model
        llm = get_chat_model()

        # Create prompt template
        prompt = PromptTemplate(
            template=JD_GENERATION_PROMPT,
            input_variables=["job_title"]
        )

        # Create the chain using StrOutputParser (avoiding .content issues)
        output_parser = StrOutputParser()
        chain = RunnableSequence(
            prompt,
            llm,
            output_parser
        )

        # Execute the chain
        result = chain.invoke({"job_title": job_title})

        return result.strip()

    except Exception as e:
        # Return a fallback if generation fails
        return f"""Job Title: {job_title}

Job Summary:
We are looking for a qualified {job_title} to join our team.

Key Responsibilities:
- Perform duties related to {job_title}
- Collaborate with cross-functional teams
- Deliver high-quality work

Required Skills:
- Relevant technical skills
- Communication skills
- Problem-solving abilities

Qualifications:
- Bachelor's degree in relevant field
- 2+ years of experience

Note: Detailed JD generation failed: {str(e)}
"""
