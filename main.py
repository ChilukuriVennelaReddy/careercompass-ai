import os
import time
import json
from collections import defaultdict
from typing import List, Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import AsyncGroq

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="CareerCompass AI")

# In-memory rate limiter: max 10 requests per minute per IP
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 10
ip_requests = defaultdict(list)


def check_rate_limit(ip: str):
    now = time.time()
    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(ip_requests[ip]) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    ip_requests[ip].append(now)


# Groq async client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("WARNING: GROQ_API_KEY is not set.")

client = AsyncGroq(api_key=groq_api_key)

# Pydantic request model
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    history: List[Dict[str, Any]] = []

class QuizGenerateRequest(BaseModel):
    role: str = Field(..., min_length=1, max_length=100)
    skills: str = Field(..., min_length=1, max_length=500)

class QuizEvaluateRequest(BaseModel):
    role: str = Field(..., min_length=1, max_length=100)
    questions: List[str]
    answers: List[str]

SYSTEM_PROMPT = """You are an AI career counselor for CareerCompass AI.
Your goal is to help university students and fresh graduates.
Follow these guidelines:
1. Ask clarifying questions before recommending careers.
2. Suggest suitable job roles and explain why those roles fit.
3. Identify skill gaps.
4. Recommend certifications and suggest projects.
5. Create personalized learning roadmaps.
6. Recommend interview preparation resources.
7. Be encouraging, professional, and concise."""


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    if not chat_req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Build message list for Groq (OpenAI-compatible format)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in chat_req.history:
        role = "user" if msg["role"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": chat_req.message})

    async def stream_generator():
        try:
            stream = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield f"data: {json.dumps({'text': delta.content})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@app.post("/api/quiz/generate")
async def generate_quiz(request: Request, req: QuizGenerateRequest):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)
    
    system_prompt = f"You are an expert technical interviewer. Generate a 5-question multiple choice quiz to test someone aiming for the role of '{req.role}' with current skills: {req.skills}. Format the output STRICTLY as a JSON object with a 'questions' array. Each question object should have 'question' (string), 'options' (array of 4 strings), and 'correct_answer' (string)."
    
    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/evaluate")
async def evaluate_quiz(request: Request, req: QuizEvaluateRequest):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)
    
    system_prompt = f"You are an expert career counselor. The user is aiming for the role of '{req.role}'. They took a quiz. Evaluate their answers and provide a detailed skill gap analysis and recommendations. Format the output STRICTLY as a JSON object with 'score' (number out of 5), 'feedback' (string), and 'skill_gaps' (array of strings)."
    
    user_content = "Questions and user answers:\n"
    for q, a in zip(req.questions, req.answers):
        user_content += f"Q: {q}\nUser's Answer: {a}\n\n"
        
    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RoadmapGenerateRequest(BaseModel):
    role: str = Field(..., min_length=1, max_length=100)
    gaps: List[str]

@app.post("/api/roadmap/generate")
async def generate_roadmap(request: Request, req: RoadmapGenerateRequest):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)
    
    system_prompt = f"You are an expert career counselor. The user is aiming for the role of '{req.role}' and has the following skill gaps: {', '.join(req.gaps)}. Create a step-by-step learning roadmap. Format the output STRICTLY as a JSON object with a 'roadmap' array. Each step should have 'title' (string) and 'description' (string)."
    
    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "static/index.html"))


@app.get("/{page}.html")
async def serve_pages(page: str):
    file_path = os.path.join(BASE_DIR, f"static/{page}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Page not found")
