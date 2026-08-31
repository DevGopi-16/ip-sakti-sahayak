import os
import re
import sys
import shutil
from contextlib import asynccontextmanager
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

from backend.rag_chain import get_rag_chain, reload_rag_chain
from backend.translate import translate_text
from backend.image_router import get_images_for_response
from backend.image_query import generate_image_query
from backend.response_service import create_response


rag_chain = None

UPLOADS_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def clean_reasoning_tags(text: str) -> str:
    if not text:
        return ""

    cleaned = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if "<think>" in cleaned.lower() and "</think>" not in cleaned.lower():
        parts = re.split(
            r"<think>",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = parts[0]

    if "here's a thinking process:" in cleaned.lower():
        parts = re.split(
            r"here's a thinking process:",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = parts[-1]

    cleaned = re.sub(
        r"</?think>",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()

    return cleaned


def process_and_reindex_task():
    global rag_chain

    try:
        print(
            "Background task started: "
            "Re-indexing documents into FAISS index..."
        )

        rag_chain = reload_rag_chain()

        print(
            "Background task completed: "
            "FAISS index updated successfully."
        )

    except Exception as e:
        print(f"Error during background re-indexing: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_chain

    print("Loading FAISS Index and initializing RAG Chain...")

    try:
        rag_chain = get_rag_chain()

        print("Backend initialization complete.")

    except Exception as e:
        print(f"Error initializing backend: {e}")
        raise e

    yield


app = FastAPI(
    title="IP-SAKTI Sahayak Backend Engine",
    lifespan=lifespan,
)


origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str = Field(
        ...,
        description="'user' or 'assistant'",
    )
    content: str


class ChatPayload(BaseModel):
    query: str
    language: str = "en"
    statute: Optional[str] = "ALL"
    chat_history: Optional[List[ChatMessage]] = []


@app.get("/")
def health_check():
    return {"status": "online"}


@app.post("/api/chat")
async def chat_endpoint(payload: ChatPayload):
    try:
        if rag_chain is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "RAG chain is not initialized. "
                    "Please restart the backend."
                ),
            )

        english_query = payload.query

        if payload.language.lower() != "en":
            english_query = translate_text(
                payload.query,
                "English",
            )

 
        history_str = ""

        if payload.chat_history:
            formatted = [
                f"{msg.role.capitalize()}: {msg.content}"
                for msg in payload.chat_history[-6:]
            ]

            history_str = "\n".join(formatted)


        invoke_input = {
            "question": english_query,
            "chat_history": history_str,
            "statute": payload.statute,
        }


        raw_answer_en = rag_chain.invoke(invoke_input)

        answer_en = clean_reasoning_tags(
            str(raw_answer_en)
        )

        image_query_result = generate_image_query(
            english_query
        )

        if image_query_result["image_needed"]:
            image_result = get_images_for_response(
                query=image_query_result["query"],
                answer=answer_en,
            )
        else:
            image_result = {
                "show_images": False,
                "search_query": "",
                "images": [],
            }

        final_answer = answer_en

        if payload.language.lower() != "en":
            final_answer = translate_text(
                answer_en,
                payload.language,
            )

        combined = create_response(
            answer=final_answer,
            images=image_result.get("images", []),
        )

        return {
            "query": payload.query,
            "language": payload.language,
            "statute": payload.statute,
            "answer": combined["answer"],

            # Multimodal image response
            "show_images": combined["show_images"],
            "search_query": image_result.get("search_query", ""),
            "images": combined["images"],
        }

    except HTTPException:
        raise

    except Exception as e:
        error_message = str(e)

        print(
            f"Internal Chat Error: {error_message}"
        )

        if (
            "RESOURCE_EXHAUSTED" in error_message
            or "429" in error_message
            or "quota" in error_message.lower()
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "AI quota limit reached for Gemini. "
                    "Please wait for the quota reset or add "
                    "a valid billing-enabled Google API key."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=error_message,
        )


@app.post("/api/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    allowed_extensions = (
        ".pdf",
        ".txt",
    )

    if not file.filename.endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid file type. Only PDF (.pdf) and "
                "Text (.txt) files are supported."
            ),
        )

    file_path = os.path.join(
        UPLOADS_DIR,
        file.filename,
    )

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        background_tasks.add_task(
            process_and_reindex_task
        )

        return {
            "status": "success",
            "filename": file.filename,
            "message": (
                f"Successfully uploaded '{file.filename}'. "
                "FAISS vector indexing is running "
                "in the background."
            ),
        }

    except Exception as e:
        print(
            f"Error during file save: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Upload file saving failed: {str(e)}"
            ),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )