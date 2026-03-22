# AI Chat Agent with ATS Resume Analysis

A production-ready FastAPI backend for an AI chat agent with ATS (Applicant Tracking System) resume analysis capabilities.

## Features

### Chat Mode
- Behaves like a normal AI assistant when no resume is uploaded
- Answers career-related questions and provides resume tips

### Resume + ATS Mode
When a PDF resume is uploaded:

**Case A: Resume + Job Description** → Performs ATS analysis

**Case B: Resume + Job Title** → Generates full Job Description → Performs ATS analysis

**Case C: Resume only** → Asks user to provide a job description or job role

### ATS Output (Strict JSON)
```json
{
  "score": 85,
  "matched_skills": ["Python", "FastAPI", "REST APIs"],
  "missing_skills": ["Docker", "Kubernetes"],
  "improvements": ["Add more quantifiable achievements", "Include cloud platform experience"]
}
```

## Tech Stack

- **Python 3.9+**
- **FastAPI** - Modern web framework
- **LangChain** - LLM orchestration
- **Groq API** - LLM provider (gpt-oss-120b)
- **pdfplumber** - PDF text extraction
- **Pydantic** - Data validation
- **uv** - Python package and project manager

## Project Structure

```
src/
├── api/
│   └── main.py           # FastAPI application
├── agent/
│   └── chat_model.py     # Chat model configuration
├── tools/
│   ├── pdf_tool.py       # PDF text extraction
│   ├── jd_tool.py        # Job description generator
│   └── ats_tool.py       # ATS analysis tool
├── chains/
│   └── ats_chain.py      # ATS LangChain pipeline
├── router/
│   └── router.py         # Routing logic
└── schemas/
    ├── request.py        # Request schemas
    └── response.py       # Response schemas
```

## Setup Instructions

### 1. Install uv (if not already installed)

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Initialize the Project

```bash
# Initialize uv project
uv init

# Create virtual environment
uv venv
```

### 3. Activate Virtual Environment

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 5. Configure Environment Variables

Edit the `.env` file:

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

Get your Groq API key from: https://console.groq.com/

### 6. Run the Server

```bash
# Run with uvicorn directly
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python src/api/main.py
```

## API Endpoints

### POST /chat

Main chat endpoint supporting both normal chat and ATS analysis modes.

#### Request (Form Data)

```
POST /chat
Content-Type: multipart/form-data

Form Fields:
- message: string (required) - User message or job description
- file: File (optional) - PDF resume file
```

#### Example: Normal Chat (No File)

```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=What are some good resume tips?"
```

**Response:**
```json
{
  "type": "chat",
  "message": "Here are some key resume tips..."
}
```

#### Example: ATS Analysis with Job Description

```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=Software Engineer with Python, Django, AWS experience required" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "type": "ats",
  "data": {
    "score": 82,
    "matched_skills": ["Python", "REST APIs", "Git"],
    "missing_skills": ["Django", "AWS"],
    "improvements": ["Add AWS certifications", "Highlight Django projects"]
  }
}
```

#### Example: ATS Analysis with Job Title

```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=AI Engineer" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "type": "ats",
  "data": {
    "score": 75,
    "matched_skills": ["Python", "Machine Learning"],
    "missing_skills": ["PyTorch", "Deep Learning"],
    "improvements": ["Add ML framework experience", "Include LLM projects"]
  }
}
```

#### Example: Resume Only (Missing JD)

```bash
curl -X POST "http://localhost:8000/chat" \
  -F "message=" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "type": "chat",
  "message": "Please provide a job description or job role for ATS analysis."
}
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-chat-ats"
}
```

### GET /

API information.

```bash
curl http://localhost:8000/
```

## Testing with Postman

1. Open Postman
2. Create a new POST request to `http://localhost:8000/chat`
3. Select "form-data" in the Body tab
4. Add key `message` with value (job title or description)
5. (Optional) Add key `file` and select a PDF file
6. Send the request

## Error Handling

The API returns structured error responses:

```json
{
  "type": "error",
  "message": "Error message here",
  "details": "Optional detailed error information"
}
```

Common errors:
- Invalid PDF file
- Empty input
- Missing GROQ_API_KEY
- JSON parsing issues (handled gracefully with fallbacks)

## Key Design Decisions

1. **StrOutputParser**: Used to avoid `.content` attribute issues with LLM responses
2. **JSON Safety**: Multiple fallback strategies for parsing JSON from LLM responses
3. **Modular Structure**: Tools, chains, and router are separated for maintainability
4. **Error Handling**: Comprehensive error handling with graceful fallbacks
5. **No Deprecated APIs**: Uses modern LangChain syntax (RunnableSequence)

## Requirements

- Python 3.9+
- Groq API key
- PDF files must be text-based (not scanned images)

## License

MIT
