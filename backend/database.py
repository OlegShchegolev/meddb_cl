from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://medical_user:medical_pass@localhost:5432/medical_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(50), primary_key=True, index=True)
    snils = Column(String(14), unique=True, index=True)  # Format: XXX-XXX-XXX XX
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    gender = Column(String(20), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    diagnosis = Column(Text)
    comment = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ultrasounds = relationship("Ultrasound", back_populates="patient", cascade="all, delete-orphan")
    mammographies = relationship("Mammography", back_populates="patient", cascade="all, delete-orphan")
    contrast_mammographies = relationship("ContrastMammography", back_populates="patient", cascade="all, delete-orphan")
    mrts = relationship("MRT", back_populates="patient", cascade="all, delete-orphan")
    histology_biopsies = relationship("HistologyBiopsy", back_populates="patient", cascade="all, delete-orphan")
    cytology_biopsies = relationship("CytologyBiopsy", back_populates="patient", cascade="all, delete-orphan")
    histology_postops = relationship("HistologyPostop", back_populates="patient", cascade="all, delete-orphan")


class Mammography(Base):
    __tablename__ = "mammographies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    study_stage = Column(Integer)  # 1-9
    affected_side = Column(String(50))  # Правая, Левая, Обе
    birads_category = Column(String(10))  # BI-RADS 0-6
    acr_density = Column(String(10))  # ACR A, B, C, D
    comparison_available = Column(Boolean, default=False)
    dynamics = Column(String(100))  # Улучшение, Без динамики, Ухудшение
    comment = Column(Text)

    patient = relationship("Patient", back_populates="mammographies")
    findings = relationship("MammographyFinding", back_populates="mammography", cascade="all, delete-orphan")


class MammographyFinding(Base):
    __tablename__ = "mammography_findings"

    id = Column(Integer, primary_key=True, index=True)
    mammography_id = Column(Integer, ForeignKey("mammographies.id"), nullable=False)
    finding_number = Column(Integer)  # 1-9
    quadrant_location = Column(String(50))  # Верхне-внутренний, Верхне-наружный и т.д.
    depth_location = Column(String(50))  # Передняя треть, Средняя треть, Задняя треть
    finding_type = Column(String(100))  # Объемное образование, Асимметрия, Кальцинаты, Сопутствующие изменения

    # Для объемного образования
    mass_shape = Column(String(50))
    mass_margin = Column(String(50))
    mass_density = Column(String(50))

    # Для асимметрии
    asymmetry_type = Column(String(50))

    # Для кальцинатов
    calcification_malignancy = Column(String(50))
    calcification_morphology = Column(String(100))
    calcification_distribution = Column(String(50))

    # Для сопутствующих изменений
    associated_feature = Column(String(100))

    # Общие поля
    size_mm = Column(String(50))  # Формат: "15x16x17"

    mammography = relationship("Mammography", back_populates="findings")


class ContrastMammography(Base):
    __tablename__ = "contrast_mammographies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    findings = Column(Text)
    comment = Column(Text)

    patient = relationship("Patient", back_populates="contrast_mammographies")


class Ultrasound(Base):
    __tablename__ = "ultrasounds"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    findings = Column(Text)
    comment = Column(Text)

    patient = relationship("Patient", back_populates="ultrasounds")


class MRT(Base):
    __tablename__ = "mrts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    findings = Column(Text)
    comment = Column(Text)

    patient = relationship("Patient", back_populates="mrts")


class HistologyBiopsy(Base):
    __tablename__ = "histology_biopsies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    findings = Column(Text)
    ihc_results = Column(Text)  # ИГХ результаты
    comment = Column(Text)

    patient = relationship("Patient", back_populates="histology_biopsies")


class CytologyBiopsy(Base):
    __tablename__ = "cytology_biopsies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    findings = Column(Text)
    comment = Column(Text)

    patient = relationship("Patient", back_populates="cytology_biopsies")


class HistologyPostop(Base):
    __tablename__ = "histology_postops"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    findings = Column(Text)
    ihc_results = Column(Text)  # ИГХ результаты
    comment = Column(Text)

    patient = relationship("Patient", back_populates="histology_postops")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()