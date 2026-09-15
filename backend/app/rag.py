import json,re,faiss
from app.documents import get_document_dir
from app.embeddings import embed_query
STOP={'the','is','a','an','of','to','in','on','for','and','or','what','why','how','does','do','are','was','were','with','from'}
def norm(s): return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9\s]',' ',s.lower())).strip()
def toks(s): return {x for x in norm(s).split() if x not in STOP}
def records(i):
 p=get_document_dir(i)/'chunks.json';return json.loads(p.read_text(encoding='utf-8')) if p.exists() else []
def search(i,q):
 rs=records(i)
 for r in rs:
  if r.get('question') and norm(r['question'])==norm(q): r.update(score=1.0,match_type='exact');return [r]
 m=re.search(r'\b(?:question|q)\s*(\d+)\b',q,re.I)
 if m:
  r=next((x for x in rs if x.get('question_number')==int(m.group(1))),None)
  if r:r.update(score=1.0,match_type='question_number');return [r]
 qt=toks(q);best=None;bs=0
 for r in rs:
  rt=toks(r.get('question','')+' '+r.get('answer',''));s=len(qt&rt)/len(qt) if qt else 0
  if s>bs:best,bs=r,s
 if best is not None and bs>=.55: best.update(score=bs,match_type='lexical');return [best]
 p=get_document_dir(i)/'index.faiss'
 if not p.exists():return []
 idx=faiss.read_index(str(p));sc,ii=idx.search(embed_query(q),min(3,len(rs)));out=[]
 for s,j in zip(sc[0],ii[0]):
  if j>=0: r=rs[int(j)];r.update(score=float(s),match_type='semantic');out.append(r)
 return out
def build_answer(rs): return rs[0].get('answer',rs[0].get('text','')) if rs else 'I could not find an answer in the selected PDF.'
