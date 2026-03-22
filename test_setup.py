"""
Quick test script to verify the setup
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")

    try:
        from src.schemas.request import ChatRequest, ATSRequest
        print("✓ Request schemas imported")
    except Exception as e:
        print(f"✗ Request schemas failed: {e}")

    try:
        from src.schemas.response import ChatResponse, ATSResponse, ATSData
        print("✓ Response schemas imported")
    except Exception as e:
        print(f"✗ Response schemas failed: {e}")

    try:
        from src.agent.chat_model import get_chat_model
        print("✓ Chat model imported")
    except Exception as e:
        print(f"✗ Chat model failed: {e}")

    try:
        from src.chains.ats_chain import get_ats_chain
        print("✓ ATS chain imported")
    except Exception as e:
        print(f"✗ ATS chain failed: {e}")

    try:
        from src.tools.jd_tool import generate_job_description
        print("✓ JD tool imported")
    except Exception as e:
        print(f"✗ JD tool failed: {e}")

    try:
        from src.tools.ats_tool import perform_ats_analysis
        print("✓ ATS tool imported")
    except Exception as e:
        print(f"✗ ATS tool failed: {e}")

    try:
        from src.router.router import process_resume_request, is_job_title
        print("✓ Router imported")
    except Exception as e:
        print(f"✗ Router failed: {e}")

    print("\nAll imports successful!")


def test_is_job_title():
    """Test the job title detection logic"""
    print("\nTesting job title detection...")

    from src.router.router import is_job_title

    test_cases = [
        ("Software Engineer", True),
        ("AI Engineer", True),
        ("Data Scientist with 5 years experience", True),
        ("Software Engineer\n\nResponsibilities:\n- Build scalable systems\n- Write clean code", False),
        ("We are looking for a Python developer with Django experience and AWS knowledge. Must have 3+ years experience.", False),
    ]

    for input_text, expected in test_cases:
        result = is_job_title(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text[:40]}...' -> {result} (expected {expected})")


if __name__ == "__main__":
    test_imports()
    test_is_job_title()
    print("\n✅ All tests completed!")
