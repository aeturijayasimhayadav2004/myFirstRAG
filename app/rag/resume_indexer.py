from sqlalchemy.orm import Session

from .. import models
from .embeddings import embed_text, add_vector


def index_resume_text(user_id: int, text: str, db: Session) -> models.Resume:
    vector = embed_text(text)
    resume = models.Resume(user_id=user_id, parsed_text=text, embedding_vector=vector.tobytes())
    db.add(resume)
    db.commit()
    db.refresh(resume)
    add_vector(resume.id, vector)
    return resume
