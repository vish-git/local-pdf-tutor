# Local PDF Tutor

A completely local multi-PDF tutor using React/TypeScript, FastAPI, PyMuPDF, Sentence Transformers and FAISS.

No OpenAI, LLM, MongoDB or cloud service.

## Backend
cd backend
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload

## Frontend
cd frontend
npm install
npm run dev

Open http://localhost:5173

Each PDF is stored separately under backend/data/documents/<document-id>/ with original.pdf, metadata.json, chunks.json, index.faiss and 300-DPI page images.

Speech-to-text is intentionally left for a later phase.
