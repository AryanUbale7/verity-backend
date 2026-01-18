from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import re
from dotenv import load_dotenv
from google import genai
from fastapi.middleware.cors import CORSMiddleware

# ===============================
# App setup
# ===============================
load_dotenv()

app = FastAPI(title="GEN-SCORE AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev ke liye ok
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")  # .env me key rakho
)

# ===============================
# Routes
# ===============================

@app.get("/")
def root():
    return {"message": "GEN-SCORE AI backend running"}


@app.get("/test-gemini")
def test_gemini():
    response = client.models.generate_content(
        model="models/gemini-pro-latest",
        contents="Say exactly: Gemini is working fine for GEN-SCORE AI"
    )
    return {"gemini_response": response.text}


# ===============================
# Evaluation API
# ===============================

class EvalRequest(BaseModel):
    prompt: str
    response: str


@app.post("/evaluate")
def evaluate(req: EvalRequest):

    scoring_prompt = f"""
You are an AI auditor.

Evaluate the following AI response.

USER PROMPT:
{req.prompt}

AI RESPONSE:
{req.response}

IMPORTANT:
- Return ONLY valid JSON
- Do NOT use markdown
- Do NOT wrap in ```json
- Do NOT add extra text
- Output must start with {{ and end with }}

JSON format:
{{
  "accuracy": "Factually Correct" | "Partially Correct" | "Factually Incorrect",
  "risk_level": "Low" | "Medium" | "High",
  "confidence": number (0-1),
  "contains_hallucination": true | false,
  "overall_rating": "Excellent" | "Good" | "Poor" | "Very Poor",
  "hallucination_signals": [],
  "short_explanation": ""
}}
"""

    try:
        # 🔹 Call Gemini
        result = client.models.generate_content(
            model="models/gemini-pro-latest",
            contents=scoring_prompt
        )

        raw_text = result.text.strip()
        clean_text = re.sub(r"```json|```", "", raw_text).strip()
        parsed = json.loads(clean_text)

        # ===============================
        # 🔢 GEN SCORE LOGIC
        # ===============================
        score = 0
        accuracy = parsed.get("accuracy", "").lower()

        if accuracy == "factually correct":
            score = 90
        elif accuracy == "partially correct":
            score = 65
        elif accuracy == "factually incorrect":
            score = 20
        else:
            score = 50

        if parsed.get("contains_hallucination") is True:
            score -= 40

        rating = parsed.get("overall_rating", "").lower()
        if rating == "excellent":
            score += 5
        elif rating == "poor":
            score -= 10
        elif rating == "very poor":
            score -= 20

        risk = parsed.get("risk_level", "").lower()
        if risk == "high":
            score -= 20
        elif risk == "medium":
            score -= 10

        score = max(0, min(100, score))
        parsed["gen_score"] = score

        # ===============================
        # 🚦 DECISION LOGIC (FIXED)
        # ===============================
        decision = "ALLOW"

        if parsed["gen_score"] < 40:
            decision = "BLOCK"
        elif parsed["risk_level"] == "Medium":
            decision = "REVIEW"

        parsed["decision"] = decision

        return parsed

    except Exception as e:
        return {
            "gen_score": 0,
            "risk_level": "High",
            "confidence": 0,
            "contains_hallucination": True,
            "hallucination_signals": ["Invalid JSON from model"],
            "overall_rating": "Very Poor",
            "decision": "BLOCK",
            "short_explanation": str(e)
        }

