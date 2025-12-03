import json
import os
from io import BytesIO
from pathlib import Path
from typing import List
from uuid import uuid4

import faiss
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel


DATA_DIR = Path("vector_store")
INDEX_PATH = DATA_DIR / "faiss.index"
DOCS_PATH = DATA_DIR / "documents.json"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"


class ChatRequest(BaseModel):
    question: str


ENV_PATH = Path(__file__).resolve().parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

fastapi_app = FastAPI(title="FAISS Chat API")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR.mkdir(exist_ok=True)


def load_index() -> faiss.Index:
    if INDEX_PATH.exists():
        return faiss.read_index(str(INDEX_PATH))
    return None


def load_documents() -> List[dict]:
    if DOCS_PATH.exists():
        with DOCS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


index = load_index()
documents = load_documents()


def persist_state() -> None:
    if index is not None:
        faiss.write_index(index, str(INDEX_PATH))
    with DOCS_PATH.open("w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    tokens = text.split()
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk = " ".join(tokens[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks or [text]


def get_openai_client() -> OpenAI:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    try:
        # Create client
        client = OpenAI(api_key=api_key)

        # Test the key with a very cheap request (models list)
        client.models.list()

        return client

    except Exception as e:
        print(f"Invalid OpenAI API key or connection error: {str(e)}" )
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY environment variable is required.")
    return OpenAI(api_key=api_key)


def embed_texts(texts: List[str]) -> List[List[float]]:
    client = get_openai_client()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def read_file_content(upload: UploadFile) -> str:
    content = upload.file.read()
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(BytesIO(content), dtype=str).fillna("")
        return df.to_csv(index=False)
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Unable to decode file as UTF-8.") from exc


@fastapi_app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    global index
    text = read_file_content(file)
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    vectors = np.array(embeddings, dtype="float32")

    if index is None:
        index = faiss.IndexFlatL2(vectors.shape[1])
    elif index.d != vectors.shape[1]:
        raise HTTPException(status_code=500, detail="Embedding size mismatch with existing index.")

    index.add(vectors)
    for chunk in chunks:
        documents.append(
            {
                "id": str(uuid4()),
                "filename": file.filename,
                "text": chunk,
            }
        )

    persist_state()
    return {"chunks_added": len(chunks)}


@fastapi_app.post("/chat")
async def chat(request: ChatRequest) -> dict:
    if index is None or index.ntotal == 0 or not documents:
        raise HTTPException(status_code=400, detail="Vector store is empty. Upload files first.")

    query_vector = np.array([embed_texts([request.question])[0]], dtype="float32")
    top_k = min(5, len(documents))
    distances, indices = index.search(query_vector, top_k)

    retrieved = []
    for idx in indices[0]:
        if idx == -1:
            continue
        retrieved.append(documents[idx])

    context_snippets = "\n\n".join(doc["text"] for doc in retrieved)
    user_prompt = (
        "Use the following document excerpts to answer the question.\n\n"
        f"{context_snippets}\n\nQuestion: {request.question}"
    )

    client = get_openai_client()
    completion = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions using the supplied context.",
            },
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    answer = completion.choices[0].message.content
    return {"answer": answer, "documents": retrieved}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:fastapi_app", host="127.0.0.1", port=8000, reload=True)
