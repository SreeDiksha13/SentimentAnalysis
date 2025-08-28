# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import torch
import uvicorn

# Detect device: 0 for first GPU, -1 for CPU
device = 0 if torch.cuda.is_available() else -1

# Use a small, fine-tuned sentiment model
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

print("Loading model... (this downloads the model if not cached)")
sentiment_pipeline = pipeline("sentiment-analysis", model=MODEL_NAME, device=device)
print("Model loaded.")

app = FastAPI(title="Sentiment API")

# Allow the React dev server origins; add production domain when deploying
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputText(BaseModel):
    text: str

@app.post("/predict")
async def predict(data: InputText):
    result = sentiment_pipeline(data.text)[0]
    return {"label": result["label"], "score": float(result["score"])}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
