from __future__ import annotations
import json,re,shutil
from pathlib import Path
import faiss,numpy as np,pymupdf
from app.embeddings import embed_texts
Q=re.compile(r'^\s*(?:Question|Q)\s*\.?\s*(\d+)\s*[:.]?\s*$',re.I)
HEADINGS={'solids','liquids','gases','melting point','boiling point','condensation','sublimation','vaporization','evaporation','change of state','inter-molecular spaces','inter-molecular forces of attraction'}
VISUAL=('diagram','shown','apparatus','table','figure','flow chart','flowchart','experiment','as shown')
def norm(s):
    s=s.replace('\x00',' ').replace('\r\n','\n').replace('\r','\n'); return '\n'.join(re.sub(r'[ \t]+',' ',x).strip() for x in s.split('\n') if x.strip()).strip()
def inline(s): return re.sub(r'\s+',' ',norm(s).replace('\n',' ')).strip()
def safe(s): return re.sub(r'[^a-z0-9]+','_',Path(s).stem.lower()).strip('_') or 'document'
def unique(root,b):
    x=b;n=2
    while (root/x).exists(): x=f'{b}_{n}';n+=1
    return x
def blocks(answer):
    out=[]; heading=None; lines=[]
    def flush():
        nonlocal heading,lines
        t=inline('\n'.join(lines))
        if t: out.append({'heading':heading,'text':t})
        heading=None;lines=[]
    for l in answer.splitlines():
        l=l.strip()
        if not l: continue
        h=re.sub(r'[:\s]+$','',l).lower()
        if h in HEADINGS: flush();heading=re.sub(r'[:\s]+$','',l)
        else: lines.append(l)
    flush(); return out or [{'heading':None,'text':inline(answer)}]
def render(doc,pdir):
    pdir.mkdir(parents=True,exist_ok=True)
    for i,page in enumerate(doc,1): page.get_pixmap(dpi=300,alpha=False).save(str(pdir/f'page_{i:03d}.png'))
def qna(doc):
    texts=[norm(p.get_text('text')) for p in doc]; starts=[]
    for pi,t in enumerate(texts):
        for li,l in enumerate(t.splitlines()):
            m=Q.match(l)
            if m: starts.append((int(m.group(1)),pi,li))
    if not starts:return []
    out=[]
    for i,(num,sp,sl) in enumerate(starts):
        ep,el=(starts[i+1][1],starts[i+1][2]) if i+1<len(starts) else (len(doc)-1,None)
        lines=[]
        for pi in range(sp,ep+1):
            ls=texts[pi].splitlines(); a=sl if pi==sp else 0;b=el if pi==ep and el is not None else len(ls);lines+=ls[a:b]
        ai=next((j for j,l in enumerate(lines) if re.match(r'^\s*Answer\s*:?',l,re.I)),None)
        if ai is None:continue
        question=inline('\n'.join(lines[1:ai])); ans=lines[ai:]
        if ans: ans[0]=re.sub(r'^\s*Answer\s*:?\s*','',ans[0],flags=re.I)
        answer=norm('\n'.join(ans)); ps=sp+1;pe=ep+1; visual=any(v in f'{question} {answer}'.lower() for v in VISUAL); ist=max(1,ps-1) if visual else ps
        out.append({'type':'question','question_number':num,'question':question,'text':answer,'answer':answer,'answer_blocks':blocks(answer),'page':ps,'page_start':ps,'page_end':pe,'page_images':[{'page':p,'url':f'/documents/{{document_id}}/pages/page_{p:03d}.png'} for p in range(ist,pe+1)],'visual_support':visual,'embedding_text':f'Question {num}. {question}\n{answer}'})
    return out
def pages(doc):
    out=[]
    for i,p in enumerate(doc,1):
        t=norm(p.get_text('text'))
        if t: out.append({'type':'page','question_number':None,'question':'','text':t,'answer':t,'answer_blocks':[{'heading':None,'text':t}],'page':i,'page_start':i,'page_end':i,'page_images':[{'page':i,'url':f'/documents/{{document_id}}/pages/page_{i:03d}.png'}],'visual_support':False,'embedding_text':t})
    return out
def ingest_pdf(pdf_path:Path,root:Path):
    root.mkdir(parents=True,exist_ok=True); did=unique(root,safe(pdf_path.name)); d=root/did; d.mkdir(); doc=pymupdf.open(str(pdf_path)); shutil.copy2(pdf_path,d/'original.pdf');render(doc,d/'pages');records=qna(doc);mode='question_answer'
    if not records: records=pages(doc);mode='page'
    for r in records:
        r['document_id']=did
        for im in r['page_images']: im['url']=im['url'].replace('{document_id}',did)
    vec=np.asarray(embed_texts([r['embedding_text'] for r in records]),dtype=np.float32); idx=faiss.IndexFlatIP(vec.shape[1]);idx.add(vec);faiss.write_index(idx,str(d/'index.faiss'))
    (d/'chunks.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    meta={'document_id':did,'filename':pdf_path.name,'title':pdf_path.stem,'pages':len(doc),'records':len(records),'extraction_mode':mode,'embedding_model':'sentence-transformers/all-MiniLM-L6-v2','status':'ready'}
    (d/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8');doc.close();return meta
