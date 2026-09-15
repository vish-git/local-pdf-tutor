import json, shutil
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parents[1]
DOCUMENTS_DIR=BASE_DIR/'data'/'documents'
def list_documents():
    DOCUMENTS_DIR.mkdir(parents=True,exist_ok=True); out=[]
    for d in sorted(DOCUMENTS_DIR.iterdir()):
        p=d/'metadata.json'
        if d.is_dir() and p.exists():
            try: out.append(json.loads(p.read_text(encoding='utf-8')))
            except Exception: pass
    return out
def get_document(i):
    p=DOCUMENTS_DIR/i/'metadata.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
def get_document_dir(i): return DOCUMENTS_DIR/i
def delete_document(i):
    d=get_document_dir(i)
    if not d.exists(): return False
    shutil.rmtree(d); return True
