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
    tnm_stage = Column(String(100))
    mkb_code = Column(String(100))
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
    study_stage = Column(Integer)
    affected_side = Column(String(50))
    birads_category = Column(String(10))
    acr_density = Column(String(10))
    comparison_available = Column(Boolean, default=False)
    dynamics = Column(String(100))
    comment = Column(Text)

    patient = relationship("Patient", back_populates="mammographies")
    findings = relationship("MammographyFinding", back_populates="mammography", cascade="all, delete-orphan")


class MammographyFinding(Base):
    __tablename__ = "mammography_findings"

    id = Column(Integer, primary_key=True, index=True)
    mammography_id = Column(Integer, ForeignKey("mammographies.id"), nullable=False)
    finding_number = Column(Integer, nullable=True)
    quadrant_location = Column(String(50))
    depth_location = Column(String(50))
    finding_type = Column(String(100))

    mass_shape = Column(String(50))
    mass_margin = Column(String(50))
    mass_density = Column(String(50))

    asymmetry_type = Column(String(50))

    calcification_malignancy = Column(String(50))
    calcification_morphology = Column(String(100))
    calcification_distribution = Column(String(50))

    associated_feature = Column(String(100))

    size_x_mm = Column(Integer)
    size_y_mm = Column(Integer)
    size_z_mm = Column(Integer)
    volume_mm3 = Column(Integer)
    size_max_mm = Column(Integer)
    size_min_mm = Column(Integer)

    mammography = relationship("Mammography", back_populates="findings")


class ContrastMammography(Base):
    __tablename__ = "contrast_mammographies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    study_stage = Column(Integer)
    affected_side = Column(String(50))
    birads_category = Column(String(10))
    acr_density = Column(String(10))
    bpe_level = Column(String(50))
    bpe_symmetry = Column(String(50))
    comparison_available = Column(Boolean, default=False)
    dynamics = Column(String(100))
    comment = Column(Text)

    patient = relationship("Patient", back_populates="contrast_mammographies")
    le_findings = relationship("ContrastMammographyLEFinding", back_populates="contrast_mammo",
                               cascade="all, delete-orphan")
    rc_findings = relationship("ContrastMammographyRCFinding", back_populates="contrast_mammo",
                               cascade="all, delete-orphan")


class ContrastMammographyLEFinding(Base):
    __tablename__ = "contrast_mammo_le_findings"

    id = Column(Integer, primary_key=True, index=True)
    contrast_mammo_id = Column(Integer, ForeignKey("contrast_mammographies.id"), nullable=False)
    finding_number = Column(Integer, nullable=True)
    quadrant_location = Column(String(50))
    depth_location = Column(String(50))
    finding_type = Column(String(100))

    mass_shape = Column(String(50))
    mass_margin = Column(String(50))
    mass_density = Column(String(50))

    asymmetry_type = Column(String(50))

    calcification_malignancy = Column(String(50))
    calcification_morphology = Column(String(100))
    calcification_distribution = Column(String(50))

    associated_features = Column(Text)

    size_x_mm = Column(Integer)
    size_y_mm = Column(Integer)
    size_z_mm = Column(Integer)
    volume_mm3 = Column(Integer)
    size_max_mm = Column(Integer)
    size_min_mm = Column(Integer)

    visible_on_rc = Column(String(10))
    rc_internal_enhancement = Column(String(50))
    rc_enhancement_degree = Column(String(50))
    rc_enhancement_intensity = Column(String(50))

    contrast_mammo = relationship("ContrastMammography", back_populates="le_findings")


class ContrastMammographyRCFinding(Base):
    __tablename__ = "contrast_mammo_rc_findings"

    id = Column(Integer, primary_key=True, index=True)
    contrast_mammo_id = Column(Integer, ForeignKey("contrast_mammographies.id"), nullable=False)
    finding_number = Column(Integer, nullable=True)
    quadrant_location = Column(String(50))
    depth_location = Column(String(50))
    finding_type = Column(String(100))

    mass_shape = Column(String(50))
    mass_margin = Column(String(50))
    enhancement_characteristic = Column(String(50))

    distribution = Column(String(50))
    internal_enhancement_pattern = Column(String(50))

    asymmetric_enhancement_pattern = Column(String(50))

    size_x_mm = Column(Integer)
    size_y_mm = Column(Integer)
    size_z_mm = Column(Integer)
    volume_mm3 = Column(Integer)
    size_max_mm = Column(Integer)
    size_min_mm = Column(Integer)
    enhancement_intensity = Column(String(50))

    contrast_mammo = relationship("ContrastMammography", back_populates="rc_findings")


class Ultrasound(Base):
    __tablename__ = "ultrasounds"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    study_stage = Column(Integer)  # Этап исследования
    menstrual_cycle_day = Column(Integer)  # День менструального цикла
    patient_position = Column(String(50))  # Положение пациента
    birads_right = Column(String(10))  # BI-RADS справа
    birads_left = Column(String(10))  # BI-RADS слева
    acr_density_right = Column(String(10))  # Плотность ACR справа
    acr_density_left = Column(String(10))  # Плотность ACR слева
    comparison_available = Column(Boolean, default=False)
    dynamics = Column(String(100))
    comment = Column(Text)

    patient = relationship("Patient", back_populates="ultrasounds")
    findings = relationship("UltrasoundFinding", back_populates="ultrasound", cascade="all, delete-orphan")
    lymph_nodes = relationship("UltrasoundLymphNode", back_populates="ultrasound", cascade="all, delete-orphan")


class UltrasoundFinding(Base):
    """Находки при УЗИ молочных желез"""
    __tablename__ = "ultrasound_findings"

    id = Column(Integer, primary_key=True, index=True)
    ultrasound_id = Column(Integer, ForeignKey("ultrasounds.id"), nullable=False)
    finding_number = Column(Integer, nullable=True)
    side = Column(String(20))  # Правая МЖ / Левая МЖ
    quadrant_location = Column(String(50))
    depth_location = Column(String(50))
    finding_type = Column(String(100))  # Объемное образование / Сопутствующие признаки

    # Для объемного образования
    mass_shape = Column(String(50))  # Округлая, Овальная, и т.д.
    spatial_orientation = Column(String(50))  # горизонтальная, вертикальная, неопределенная
    mass_margin = Column(String(50))  # Ровные четкие, Неровные и т.д.
    mass_boundary = Column(String(100))  # четкие (капсула определяется), нечеткие и т.д.

    # Описание образования
    echogenicity = Column(String(50))  # анэхогенное, гипоэхогенное, гиперэхогенное, изоэхогенное
    structure = Column(String(100))  # однородная, неоднородная и варианты
    acoustic_effects = Column(String(100))  # нет, дорсальное усиление, латеральные тени и т.д.
    vascularization_type = Column(String(50))  # Аваскулярный, Васкуляризация внутри, Периферическая
    surrounding_tissue = Column(String(100))  # нарушение целостности, утолщение подкожной клетчатки и т.д.

    # Размеры
    size_x_mm = Column(Integer)
    size_y_mm = Column(Integer)
    size_z_mm = Column(Integer)
    volume_mm3 = Column(Integer)

    # Для сопутствующих признаков
    associated_feature_type = Column(String(100))  # Втяжение/утолщение/отек кожи, Втяжение соска и т.д.

    ultrasound = relationship("Ultrasound", back_populates="findings")


class UltrasoundLymphNode(Base):
    """Лимфоузлы при УЗИ"""
    __tablename__ = "ultrasound_lymph_nodes"

    id = Column(Integer, primary_key=True, index=True)
    ultrasound_id = Column(Integer, ForeignKey("ultrasounds.id"), nullable=False)
    finding_number = Column(Integer, nullable=True)
    side = Column(String(20))  # Правая МЖ / Левая МЖ
    has_changes = Column(String(10))  # Да / Нет

    # Группа ЛУ
    lymph_node_group = Column(String(100))  # Надключичные, Подключичные и т.д.

    # Характеристики ЛУ
    shape = Column(String(50))  # Округлая, Овальная, Неправильная
    margin = Column(String(50))  # Ровные четкие, Неровные и варианты
    boundary = Column(String(100))  # четкие, нечеткие, капсула и т.д.

    # Размеры
    size_x_mm = Column(Integer)
    size_y_mm = Column(Integer)
    size_z_mm = Column(Integer)

    # Эхогенность
    medulla_echogenicity = Column(String(50))  # Эхогенность мозгового отдела
    cortex_echogenicity = Column(String(50))  # Эхогенность коркового отдела
    has_widened_cortex = Column(String(10))  # Да / Нет

    # Васкуляризация
    vascularization_type = Column(String(50))  # Аваскулярный, Васкуляризация внутри ЛУ и т.д.

    # Характеристика гиперплазии
    hyperplasia_type = Column(String(50))  # Доброкачественная / Злокачественная

    ultrasound = relationship("Ultrasound", back_populates="lymph_nodes")


class MRT(Base):
    __tablename__ = "mrts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    study_stage = Column(Integer)
    menstrual_cycle_day = Column(Integer)
    birads_right = Column(String(10))
    birads_left = Column(String(10))
    acr_density_right = Column(String(10))
    acr_density_left = Column(String(10))
    bpe_level = Column(String(50))
    bpe_symmetry = Column(String(50))
    comparison_available = Column(Boolean, default=False)
    dynamics = Column(String(100))
    comment = Column(Text)

    patient = relationship("Patient", back_populates="mrts")
    findings = relationship("MRTFinding", back_populates="mrt", cascade="all, delete-orphan")
    lymph_nodes = relationship("MRTLymphNode", back_populates="mrt", cascade="all, delete-orphan")


# Добавьте новые классы после MRT:

class MRTFinding(Base):
    """Находки при МРТ молочных желез"""
    __tablename__ = "mrt_findings"

    id = Column(Integer, primary_key=True, index=True)
    mrt_id = Column(Integer, ForeignKey("mrts.id"), nullable=False)
    finding_number = Column(Integer, nullable=True)
    side = Column(String(20))
    quadrant_location = Column(String(50))
    depth_location = Column(String(50))
    finding_type = Column(
        String(100))  # Образование, Очаг, Зона неопухолевого контрастирования (NME), Сопутствующие признаки

    # Для образования/очага
    mass_shape = Column(String(50))
    mass_margin = Column(String(50))

    # Размеры
    size_x_mm = Column(Integer)
    size_y_mm = Column(Integer)
    size_z_mm = Column(Integer)
    volume_mm3 = Column(Integer)

    # Характеристики
    t2_signal = Column(String(50))  # Гиперинтенсивный, негиперинтенсивный, Изоинтенсивный
    enhancement_characteristics = Column(String(100))  # Гомогенное, Гетерогенное и т.д.
    kinetics = Column(String(50))  # 1й тип кривой, 2й тип кривой, 3й тип кривой
    dwi_signal = Column(String(50))  # Высокий, Низкий, Изоинтенсивный
    adc_signal = Column(String(100))  # Низкий (светлый на ADC = темный на карте), Высокий
    adc_value = Column(Float)  # Значение ADC
    invasion_signs = Column(String(100))  # Вовлечение, перифокальный отёк

    # Для зоны неопухолевого контрастирования (NME)
    nme_distribution = Column(String(50))  # Фокальное, Линейное, Сегментарное и т.д.
    nme_enhancement = Column(String(100))  # Гомогенное, Гетерогенное и т.д.

    mrt = relationship("MRT", back_populates="findings")


class MRTLymphNode(Base):
    """Лимфоузлы при МРТ"""
    __tablename__ = "mrt_lymph_nodes"

    id = Column(Integer, primary_key=True, index=True)
    mrt_id = Column(Integer, ForeignKey("mrts.id"), nullable=False)
    finding_number = Column(Integer, nullable=True)
    side = Column(String(20))
    has_changes = Column(String(10))  # Да / Нет

    # Группа ЛУ
    lymph_node_group = Column(String(100))

    # Характеристики ЛУ
    shape = Column(String(100))  # Округлая / выпуклая и т.д.
    contour = Column(String(100))  # Ровные, Неровные: волнистые и т.д.
    size_cortical_mm = Column(Integer)  # Размер (наибольший кортикальный), мм

    # Структура и контрастирование
    structure = Column(Text)  # Сохраненные ворота и т.д.
    enhancement_intensity = Column(String(100))  # Умеренное, гомогенное и т.д.
    kinetics = Column(String(50))  # 1й тип кривой, 2й тип кривой, 3й тип кривой

    # DWI и ADC
    dwi_signal = Column(String(50))  # Высокий, Низкий, Изоинтенсивный
    adc_signal = Column(String(100))  # Низкий, Высокий
    adc_value = Column(Float)  # Значение ADC

    mrt = relationship("MRT", back_populates="lymph_nodes")


class HistologyBiopsy(Base):
    __tablename__ = "histology_biopsies"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey("patients.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    findings = Column(Text)
    ihc_results = Column(Text)
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
    ihc_results = Column(Text)
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