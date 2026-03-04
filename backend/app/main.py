from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from database import SessionLocal, engine, Base
from models.models import Conversation

from services.ollama_service import ask_model
from services.embedding_service import get_embedding
from utils.similarity import cosine_similarity

import json
import time
from sqlalchemy.exc import OperationalError

app = FastAPI()

@app.on_event("startup")
def init_db():
    max_retries = 30
    retry_delay = 2

    for _ in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            time.sleep(retry_delay)

    raise RuntimeError("No se pudo conectar a PostgreSQL durante el startup")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers="*"
)

class Question(BaseModel):
    prompt: str


@app.post("/ask")
def ask_ai(question: Question):
    db = SessionLocal()

    try:
        response = ask_model(question.prompt)
        embedding = get_embedding(question.prompt)

        convo = Conversation(
            prompt=question.prompt,
            response=response,
            embedding=json.dumps(embedding)
        )

        db.add(convo)
        db.commit()
        db.refresh(convo)

        return {"response": response}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()



@app.post("/search")
def search_similar(query: str):
    db = SessionLocal()
    query_embedding = get_embedding(query)

    conversations = db.query(Conversation).all()

    results = []

    for convo in conversations:
        stored_embedding = json.loads(convo.embedding)
        score = cosine_similarity(query_embedding, stored_embedding)

        results.append({
            "prompt": convo.prompt,
            "response": convo.response,
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:3]