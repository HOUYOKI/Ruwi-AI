from sqlalchemy.orm import Session
from app.models import DocumentChunk
class RAGService:
    def retrieve(self,db:Session,query:str,limit:int=5):
        words={w.lower() for w in query.split() if len(w)>2}
        rows=db.query(DocumentChunk).limit(200).all()
        ranked=[]
        for row in rows:
            score=sum(1 for w in words if w in row.content.lower())
            if score: ranked.append((score,row))
        return [r for _,r in sorted(ranked,key=lambda x:x[0],reverse=True)[:limit]]
