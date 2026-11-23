from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bfsi_risk.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    analyses = relationship("RiskAnalysis", back_populates="owner")


class RiskAnalysis(Base):
    __tablename__ = "risk_analyses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String, nullable=False)
    ticker = Column(String)
    overall_risk_score = Column(Float)
    market_risk_score = Column(Float)
    sentiment_score = Column(Float)
    financial_risk_score = Column(Float)
    compliance_risk_score = Column(Float)
    risk_level = Column(String)  # LOW / MEDIUM / HIGH / CRITICAL
    summary = Column(Text)
    market_analysis = Column(Text)
    sentiment_analysis = Column(Text)
    financial_analysis = Column(Text)
    compliance_analysis = Column(Text)
    debate_analysis = Column(Text, nullable=True)
    guardrails_result = Column(Text, nullable=True)
    adjusted_risk_score = Column(Float, nullable=True)
    trust_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="analyses")
    chat_messages = relationship("ChatMessage", back_populates="analysis")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("risk_analyses.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis = relationship("RiskAnalysis", back_populates="chat_messages")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    company = Column(String)
    doc_type = Column(String)  # annual_report, 10k, earnings, etc.
    chroma_collection = Column(String)
    pages = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
