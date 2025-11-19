from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..db import get_db
from ..rag.resume_indexer import index_resume_text

router = APIRouter(tags=["resume"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/resume")
def get_resume_page(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.user_id == current_user.id)
        .order_by(models.Resume.created_at.desc())
        .first()
    )
    skills = db.query(models.Skill).filter(models.Skill.user_id == current_user.id).all()
    return templates.TemplateResponse(
        "resume.html",
        {"request": request, "user": current_user, "resume_text": resume.parsed_text if resume else "", "skills": skills},
    )


@router.post("/resume")
def upload_resume(
    request: Request,
    text: str = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Resume text required")
    index_resume_text(user_id=current_user.id, text=text, db=db)
    return RedirectResponse(url="/resume", status_code=303)


@router.get("/skills", response_model=list[schemas.SkillOut])
def list_skills(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    skills = db.query(models.Skill).filter(models.Skill.user_id == current_user.id).all()
    return skills


@router.post("/skills", response_model=schemas.SkillOut)
def add_skill(skill_in: schemas.SkillIn, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    skill = models.Skill(user_id=current_user.id, **skill_in.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id, models.Skill.user_id == current_user.id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return {"message": "Skill deleted"}
