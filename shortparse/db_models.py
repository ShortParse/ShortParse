import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from shortparse.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False)
    premium_tier = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    linked_accounts = relationship("LinkedAccount", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user")


class LinkedAccount(Base):
    __tablename__ = "linked_accounts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # "warcraftlogs", "patreon", etc.
    provider_user_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="linked_accounts")


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(String, nullable=False, default="queued")
    report_url = Column(String, nullable=False)
    report_code = Column(String, nullable=False)
    result_path = Column(String, nullable=True)
    error = Column(String, nullable=True)
    progress = Column(Integer, default=0)
    current_step = Column(String, nullable=True)
    logs = Column(JSON, default=list)  # SQLite natively supports JSON type in modern versions!
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="jobs")
