from pathlib import Path
import shutil
from fastapi import FastAPI,File,HTTPException,UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.documents import DOCUMENTS_DIR,delete_document,get_document,list_documents
from app.models import AskRequest,AskResponse,DocumentResponse,Source
from app.rag import build_answer,search
from services.ingest import ingest_pdf
app=FastAPI(title='Local PDF Tutor')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
DOCUMENTS_DIR.mkdir(parents=True,exist_ok=True);app.mount('/documents',StaticFiles(directory=str(DOCUMENTS_DIR)),name='documents')
@app.get('/health')
def health():return {'status':'ok'}
@app.get('/api/documents',response_model=list[DocumentResponse])
def docs():return list_documents()
@app.post('/api/documents/upload',response_model=DocumentResponse)
async def upload(file:UploadFile=File(...)):
 if not file.filename or not file.filename.lower().endswith('.pdf'):raise HTTPException(400,'Only PDF files are supported.')
 tmp=DOCUMENTS_DIR.parent/'uploads';tmp.mkdir(parents=True,exist_ok=True);p=tmp/file.filename
 try:
  with p.open('wb') as f:shutil.copyfileobj(file.file,f)
  return ingest_pdf(p,DOCUMENTS_DIR)
 except Exception as e:raise HTTPException(500,f'PDF ingestion failed: {e}') from e
 finally:p.unlink(missing_ok=True)
@app.delete('/api/documents/{document_id}')
def remove(document_id:str):
 if not delete_document(document_id):raise HTTPException(404,'Document not found.')
 return {'status':'deleted','document_id':document_id}
@app.post('/api/doubt',response_model=AskResponse)
def doubt(req:AskRequest):
 if not get_document(req.document_id):raise HTTPException(404,'Document not found.')
 rs=search(req.document_id,req.question);return {'answer':build_answer(rs),'sources':[Source(**r) for r in rs]}
