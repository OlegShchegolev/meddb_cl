from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://medical_user:medical_pass@localhost:5432/medical_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(50), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(Text)

    mammographies = relationship("Mammography", back_populates="patient", cascade="all, delete-orphan")
    ultrasounds = relationship("Ultrasound", back_populates="patient", cascade="all, delete-orphan")
    mrts = relationship("MRT", back_populates="patient", cascade="all, delete-orphan")


class Mammography(Base):
    __tablename__ = "mammographies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    breast_density = Column(String(50))
    findings = Column(Text)
    birads_score = Column(Integer)
    notes = Column(Text)

    patient = relationship("Patient", back_populates="mammographies")


class Ultrasound(Base):
    __tablename__ = "ultrasounds"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    organ = Column(String(100))
    findings = Column(Text)
    measurements = Column(String(200))
    notes = Column(Text)

    patient = relationship("Patient", back_populates="ultrasounds")


class MRT(Base):
    __tablename__ = "mrts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    body_part = Column(String(100))
    contrast_used = Column(String(50))
    findings = Column(Text)
    impression = Column(Text)
    notes = Column(Text)

    patient = relationship("Patient", back_populates="mrts")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()