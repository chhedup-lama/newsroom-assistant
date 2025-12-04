# Chhedup AI Workspace

Bring your documents, get trusted answers. Chhedup pairs a FastAPI backend for ingestion and vector search with a React UI so teams can upload knowledge, query it conversationally, and cite the sources every time.

---

## Features

- Document intake: upload spreadsheets or UTF-8 text, automatically chunked and embedded into FAISS.
- Context-aware chat: ask questions and receive answers grounded in top matching chunks.
- Modern UI: Vite + React single-page experience with a startup look.
- Local first: everything runs locally; point the UI at `http://127.0.0.1:8000`.

---

## Tech Stack

| Layer   | Stack                             | Purpose                            |
|---------|-----------------------------------|------------------------------------|
| Backend | FastAPI, FAISS, OpenAI embeddings | File ingestion, vector store, chat |
| UI      | React 18, Vite, React Router      | Upload and chat experience         |
| Storage | Local filesystem (`vector_store/`) | Persist FAISS index across runs    |

---

## Prerequisites

- Python 3.10+
- Node.js 18+ with npm
- OpenAI API key (embeddings and chat access)

---

## Quick Start

```bash
git clone <repo>
cd Chhedup
```

### 1. Backend (FastAPI + FAISS)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
echo OPENAI_API_KEY=your_key_here > .env
uvicorn main:app --reload
```

**API Endpoints**

- `POST /upload`: multipart field `file`; accepts `.xls`, `.xlsx`, or UTF-8 text, embeds, and saves chunks to `vector_store/`.
- `POST /chat`: JSON body `{"question": "..."}`; retrieves the top five chunks from FAISS and returns an OpenAI-powered answer.

### 2. Frontend (React + Vite)

```bash
cd UI
npm install
npm run dev
```

- Dev server: `http://127.0.0.1:5173`
- Ensure FastAPI is running for API calls
- Production build: `npm run build && npm run preview`

---

## Project Structure

- `main.py` - FastAPI app exposing `/upload` and `/chat`.
- `vector_store/` - persisted FAISS index.
- `UI/` - React + Vite frontend (see `src/App.jsx` and `src/App.css`).
- `requirements.txt` - backend dependencies.
- `.env` - local environment variables (e.g., `OPENAI_API_KEY`).

---

## Testing Checklist

- Upload a sample `.xlsx` or `.txt` and confirm "Upload successful."
- Ask a question referencing the uploaded content; verify the response cites it.
- Build the UI for production: `cd UI && npm run build`.

---

## Contributions

Issues and pull requests are welcome. Please lint and document changes, and include repro steps for bug reports.

---

## License

MIT (or replace with your preferred license).
