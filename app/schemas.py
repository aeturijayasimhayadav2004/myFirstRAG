from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class ResumeIn(BaseModel):
    text: str


class ResumeOut(BaseModel):
    id: int
    parsed_text: str
    created_at: datetime

    class Config:
        orm_mode = True


class SkillIn(BaseModel):
    name: str
    level: Optional[str] = None
    category: Optional[str] = None


class SkillOut(SkillIn):
    id: int

    class Config:
        orm_mode = True


class JobPreferenceIn(BaseModel):
    preferred_titles: Optional[str] = None
    locations: Optional[str] = None
    remote_only: Optional[bool] = False
    min_salary: Optional[int] = None
    job_type: Optional[str] = None
    auto_apply_enabled: Optional[bool] = False
    max_applications_per_day: Optional[int] = 3
    providers_enabled: Optional[str] = None


class JobPreferenceOut(JobPreferenceIn):
    id: int

    class Config:
        orm_mode = True


class MatchOut(BaseModel):
    id: int
    job_id: int
    similarity_score: float
    status: str
    reason: Optional[str]
    created_at: datetime
    job_title: Optional[str]
    job_company: Optional[str]
    job_location: Optional[str]


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    status: str
    submitted_at: Optional[datetime]
    error_message: Optional[str]
    job_title: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
