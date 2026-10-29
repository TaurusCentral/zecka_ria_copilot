from __future__ import annotations
from pathlib import Path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EvidenceRAG:
    def __init__(self, folder: str):
        self.docs=[]
        for p in sorted(Path(folder).glob("*.md")):
            text=p.read_text(encoding="utf-8")
            source="unknown"
            page="n/a"
            m=re.search(r"^SOURCE:\s*(.+)$",text,re.M); source=m.group(1).strip() if m else source
            m=re.search(r"^PAGE:\s*(.+)$",text,re.M); page=m.group(1).strip() if m else page
            body=re.sub(r"^(SOURCE|PAGE):.*$","",text,flags=re.M).strip()
            for i,chunk in enumerate(re.split(r"\n\s*\n",body)):
                if len(chunk.strip())>40:
                    self.docs.append({"text":chunk.strip(),"source":source,"page":page,"file":p.name,"chunk":i})
        self.vec=TfidfVectorizer(stop_words="english",ngram_range=(1,2))
        self.mat=self.vec.fit_transform([d["text"] for d in self.docs]) if self.docs else None

    def retrieve(self,q:str,k=4,min_score=.05):
        if self.mat is None: return []
        qv=self.vec.transform([q]); s=cosine_similarity(qv,self.mat)[0]
        idx=s.argsort()[::-1][:k]
        return [dict(self.docs[i],score=float(s[i])) for i in idx if s[i]>=min_score]

    def answer(self,q:str,k=4):
        hits=self.retrieve(q,k)
        if not hits:
            return {"answer":"Insufficient evidence in the indexed documents. I will not invent a fund fact.","citations":[],"abstained":True}
        bullets=[]; cites=[]
        for h in hits:
            bullets.append(h["text"])
            cites.append({"source":h["source"],"page":h["page"],"file":h["file"],"score":h["score"]})
        return {"answer":"\n\n".join(bullets),"citations":cites,"abstained":False}
