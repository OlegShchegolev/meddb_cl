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
    snils = Column(String(14), unique=True, index=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    gender = Column(String(20), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    diagnosis = Column(Text)
    tnm_stage = Column(String(100))  # Новое поле: Стадия по TNM
    mkb_code = Column(String(100))  # Новое поле: Код по МКБ
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
    size_x_mm = Column(Integer)   # Размеры
    size_y_mm = Column(Integer)   # Размеры
    size_z_mm = Column(Integer)   # Размеры
    # volume_mm3 = Column(Integer)  # Размеры

    mammography = relationship("Mammography", back_populates="findings")


class ContrastMammography(Base):
    __tablename__ = "contrast_mammographies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    study_stage = Column(Integer)  # Этап исследования 1-9
    affected_side = Column(String(50))  # Сторона поражения
    birads_category = Column(String(10))  # BI-RADS
    acr_density = Column(String(10))  # Плотность по ACR
    bpe_level = Column(String(50))  # Степень фонового контрастирования паренхимы (BPE)
    bpe_symmetry = Column(String(50))  # Симметрия фонового контрастирования
    comparison_available = Column(Boolean, default=False)  # Сравнение с предыдущими
    dynamics = Column(String(100))  # Динамика
    comment = Column(Text)

    patient = relationship("Patient", back_populates="contrast_mammographies")
    le_findings = relationship("ContrastMammographyLEFinding", back_populates="contrast_mammo",
                               cascade="all, delete-orphan")
    rc_findings = relationship("ContrastMammographyRCFinding", back_populates="contrast_mammo",
                               cascade="all, delete-orphan")


class ContrastMammographyLEFinding(Base):
    """Находки на LE (Low Energy) при контрастной маммографии"""
    __tablename__ = "contrast_mammo_le_findings"

    id = Column(Integer, primary_key=True, index=True)
    contrast_mammo_id = Column(Integer, ForeignKey("contrast_mammographies.id"), nullable=False)
    finding_number = Column(Integer)  # 1-9
    quadrant_location = Column(String(50))
    depth_location = Column(String(50))
    finding_type = Column(String(100))  # Тип находки на LE

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
    associated_features = Column(Text)  # Список с множественным выбором (JSON)

    size_x_mm = Column(Integer)   # Размеры
    size_y_mm = Column(Integer)   # Размеры
    size_z_mm = Column(Integer)   # Размеры
    # volume_mm3 = Column(Integer)  # Размеры

    # Определяется ли на RC
    visible_on_rc = Column(String(10))  # Да/Нет
    rc_internal_enhancement = Column(String(50))  # Паттерн внутреннего контрастирования
    rc_enhancement_degree = Column(String(50))  # Степень контрастирования
    rc_enhancement_intensity = Column(String(50))  # Интенсивность контрастирования

    contrast_mammo = relationship("ContrastMammography", back_populates="le_findings")


class ContrastMammographyRCFinding(Base):
    """Находки на RC (Recombined), не определяющиеся на LE"""
    __tablename__ = "contrast_mammo_rc_findings"

    id = Column(Integer, primary_key=True, index=True)
    contrast_mammo_id = Column(Integer, ForeignKey("contrast_mammographies.id"), nullable=False)
    finding_number = Column(Integer)  # 1-9
    quadrant_location = Column(String(50))
    depth_location = Column(String(50))
    finding_type = Column(String(100))  # Тип находки на RC

    # Для объемного образования
    mass_shape = Column(String(50))
    mass_margin = Column(String(50))
    enhancement_characteristic = Column(String(50))  # Характеристика контрастирования

    # Для зоны контрастирования без образования
    distribution = Column(String(50))
    internal_enhancement_pattern = Column(String(50))  # Паттерн внутреннего усиления

    # Для зоны асимметричного контрастирования
    asymmetric_enhancement_pattern = Column(String(50))

    size_x_mm = Column(Integer)   # Размеры
    size_y_mm = Column(Integer)   # Размеры
    size_z_mm = Column(Integer)   # Размеры
    volume_mm3 = Column(Integer)  # Размеры
    size_max_mm = Column(Integer) # Размеры
    size_min_mm = Column(Integer) # Размеры
    enhancement_intensity = Column(String(50))  # Интенсивность контрастирования

    contrast_mammo = relationship("ContrastMammography", back_populates="rc_findings")


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