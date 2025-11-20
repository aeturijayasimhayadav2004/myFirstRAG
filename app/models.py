from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    JSON,
    LargeBinary,
)
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user")
    skills = relationship("Skill", back_populates="user")
    preferences = relationship("JobPreference", uselist=False, back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String)
    parsed_text = Column(Text)
    embedding_vector = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    level = Column(String)
    category = Column(String)

    user = relationship("User", back_populates="skills")


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preferred_titles = Column(Text)
    locations = Column(Text)
    remote_only = Column(Boolean, default=False)
    min_salary = Column(Integer)
    job_type = Column(String)
    auto_apply_enabled = Column(Boolean, default=False)
    max_applications_per_day = Column(Integer, default=3)
    providers_enabled = Column(Text)

    user = relationship("User", back_populates="preferences")


class JobSource(Base):
    __tablename__ = "job_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    base_url = Column(String)


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("job_sources.id"))
    external_job_id = Column(String, index=True)
    title = Column(String)
    company = Column(String)
    location = Column(String)
    url = Column(String)
    description = Column(Text)
    raw_data = Column(JSON)
    embedding_vector = Column(LargeBinary)
    posted_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("JobSource")


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("job_postings.id"))
    similarity_score = Column(String)
    status = Column(String, default="PENDING")
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("JobPosting")
    user = relationship("User")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("job_postings.id"))
    status = Column(String, default="DRAFT")
    application_payload = Column(JSON)
    submitted_at = Column(DateTime)
    error_message = Column(String)

    job = relationship("JobPosting")
    user = relationship("User")


class ProviderAccount(Base):
    __tablename__ = "provider_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
