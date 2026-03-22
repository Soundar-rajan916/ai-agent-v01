"""
ATS Analysis Tool
Performs ATS analysis by calling the ATS chain
"""
import json
import re
from typing import Dict, Any
from src.chains.ats_chain import get_ats_chain


def perform_ats_analysis(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Perform ATS analysis on resume against job description.

    Args:
        resume_text: Extracted text from resume
        job_description: Job description text

    Returns:
        dict: ATS analysis results with score, matched_skills, missing_skills, improvements
    """
    try:
        # Get the ATS chain
        chain = get_ats_chain()

        # Prepare input
        input_data = {
            "resume_text": resume_text,
            "job_description": job_description
        }

        # Execute the chain
        result = chain.invoke(input_data)

        # Parse the result safely
        ats_result = parse_ats_result(result)

        return ats_result

    except Exception as e:
        # Return a safe fallback result on error
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": ["Error analyzing resume"],
            "improvements": [f"Analysis failed: {str(e)}"]
        }


def parse_ats_result(result: str) -> Dict[str, Any]:
    """
    Safely parse ATS result from LLM output.

    Args:
        result: Raw string output from LLM (should be JSON)

    Returns:
        dict: Parsed ATS result with defaults for missing fields
    """
    default_result = {
        "score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "improvements": []
    }

    if not result or not result.strip():
        return default_result

    try:
        # Try direct JSON parsing first
        result = result.strip()
        parsed = json.loads(result)
        return validate_ats_result(parsed)

    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON from markdown
        try:
            # Look for JSON in code blocks
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                parsed = json.loads(json_str)
                return validate_ats_result(parsed)

            # Look for JSON between curly braces
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return validate_ats_result(parsed)

            # If all else fails, try to parse line by line
            return parse_non_json_result(result)

        except Exception:
            return default_result


def validate_ats_result(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize ATS result dictionary.

    Args:
        parsed: Parsed dictionary

    Returns:
        dict: Validated and normalized result
    """
    result = {
        "score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "improvements": []
    }

    # Validate score
    if "score" in parsed:
        try:
            score = int(parsed["score"])
            result["score"] = max(0, min(100, score))  # Clamp between 0-100
        except (ValueError, TypeError):
            result["score"] = 0

    # Validate matched_skills
    if "matched_skills" in parsed and isinstance(parsed["matched_skills"], list):
        result["matched_skills"] = [
            str(skill) for skill in parsed["matched_skills"]
            if skill
        ]

    # Validate missing_skills
    if "missing_skills" in parsed and isinstance(parsed["missing_skills"], list):
        result["missing_skills"] = [
            str(skill) for skill in parsed["missing_skills"]
            if skill
        ]

    # Validate improvements
    if "improvements" in parsed and isinstance(parsed["improvements"], list):
        result["improvements"] = [
            str(imp) for imp in parsed["improvements"]
            if imp
        ]

    return result


def parse_non_json_result(result: str) -> Dict[str, Any]:
    """
    Attempt to parse non-JSON formatted result.

    Args:
        result: Raw text output

    Returns:
        dict: Extracted information
    """
    result_dict = {
        "score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "improvements": []
    }

    lines = result.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to find score
        score_match = re.search(r'["\']?score["\']?\s*[:=]\s*(\d+)', line, re.IGNORECASE)
        if score_match:
            result_dict["score"] = int(score_match.group(1))
            continue

        # Detect sections
        lower_line = line.lower()
        if 'matched' in lower_line and 'skill' in lower_line:
            current_section = "matched_skills"
            continue
        elif 'missing' in lower_line and 'skill' in lower_line:
            current_section = "missing_skills"
            continue
        elif 'improvement' in lower_line:
            current_section = "improvements"
            continue

        # Extract list items
        if current_section and (line.startswith('-') or line.startswith('*') or re.match(r'^\d+\.', line)):
            item = re.sub(r'^[-*\d.)\s]+', '', line).strip()
            if item:
                result_dict[current_section].append(item)

    return result_dict
