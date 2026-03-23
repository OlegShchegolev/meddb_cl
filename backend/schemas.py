from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


# Patient Schemas
class PatientBase(BaseModel):
    snils: Optional[str] = None
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    gender: str
    date_of_birth: date
    diagnosis: Optional[str] = None
    tnm_stage: Optional[str] = None
    mkb_code: Optional[str] = None
    comment: Optional[str] = None


class PatientCreate(BaseModel):
    id: str
    snils: Optional[str] = None
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    gender: str
    date_of_birth: date
    diagnosis: Optional[str] = None
    tnm_stage: Optional[str] = None
    mkb_code: Optional[str] = None
    comment: Optional[str] = None


class PatientUpdate(PatientBase):
    pass


class Patient(PatientBase):
    id: str
    last_updated: datetime

    class Config:
        from_attributes = True


# Mammography Finding Schemas
class MammographyFindingBase(BaseModel):
    finding_number: Optional[int] = None
    affected_side: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    finding_type: Optional[str] = None
    mass_shape: Optional[str] = None
    mass_margin: Optional[str] = None
    mass_density: Optional[str] = None
    asymmetry_type: Optional[str] = None
    calcification_in_structure: Optional[str] = None
    calcification_malignancy: Optional[str] = None
    calcification_morphology: Optional[str] = None
    calcification_distribution: Optional[str] = None
    associated_feature: Optional[str] = None
    size_x_mm: Optional[int] = None
    size_y_mm: Optional[int] = None
    size_z_mm: Optional[int] = None
    volume_mm3: Optional[int] = None
    size_max_mm: Optional[int] = None
    size_min_mm: Optional[int] = None
    comparison_available: Optional[bool] = False
    dynamics: Optional[str] = None
    comment: Optional[str] = None


class MammographyFindingCreate(MammographyFindingBase):
    mammography_id: int


class MammographyFinding(MammographyFindingBase):
    id: int
    mammography_id: int

    class Config:
        from_attributes = True


# Mammography Schemas
class MammographyBase(BaseModel):
    exam_date: date
    study_stage: Optional[int] = None
    menstrual_cycle_day: Optional[str] = None
    birads_category_left: Optional[str] = None
    birads_category_right: Optional[str] = None
    acr_density_left: Optional[str] = None
    acr_density_right: Optional[str] = None


class MammographyCreate(MammographyBase):
    patient_id: str


class MammographyUpdate(MammographyBase):
    patient_id: str


class Mammography(MammographyBase):
    id: int
    patient_id: str
    findings: List[MammographyFinding] = []

    class Config:
        from_attributes = True


# Contrast Mammography LE Finding Schemas
class ContrastMammographyLEFindingBase(BaseModel):
    finding_number: Optional[int] = None
    affected_side: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    finding_type: Optional[str] = None
    mass_shape: Optional[str] = None
    mass_margin: Optional[str] = None
    mass_density: Optional[str] = None
    asymmetry_type: Optional[str] = None
    calcification_in_structure: Optional[str] = None
    calcification_malignancy: Optional[str] = None
    calcification_morphology: Optional[str] = None
    calcification_distribution: Optional[str] = None
    contrast_type: Optional[str] = None
    associated_features: Optional[str] = None
    size_x_mm: Optional[int] = None
    size_y_mm: Optional[int] = None
    size_z_mm: Optional[int] = None
    volume_mm3: Optional[int] = None
    size_max_mm: Optional[int] = None
    size_min_mm: Optional[int] = None
    visible_on_rc: Optional[str] = None
    rc_internal_enhancement: Optional[str] = None
    rc_enhancement_degree: Optional[str] = None
    rc_enhancement_intensity: Optional[str] = None
    comparison_available: Optional[bool] = False
    dynamics: Optional[str] = None
    # comment: Optional[str] = None


class ContrastMammographyLEFindingCreate(ContrastMammographyLEFindingBase):
    contrast_mammo_id: int


class ContrastMammographyLEFinding(ContrastMammographyLEFindingBase):
    id: int
    contrast_mammo_id: int

    class Config:
        from_attributes = True


# Contrast Mammography RC Finding Schemas
class ContrastMammographyRCFindingBase(BaseModel):
    finding_number: Optional[int] = None
    affected_side: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    finding_type: Optional[str] = None
    mass_shape: Optional[str] = None
    mass_margin: Optional[str] = None
    enhancement_characteristic: Optional[str] = None
    distribution: Optional[str] = None
    internal_enhancement_pattern: Optional[str] = None
    asymmetric_enhancement_pattern: Optional[str] = None
    size_x_mm: Optional[int] = None
    size_y_mm: Optional[int] = None
    size_z_mm: Optional[int] = None
    volume_mm3: Optional[int] = None
    size_max_mm: Optional[int] = None
    size_min_mm: Optional[int] = None
    enhancement_intensity: Optional[str] = None
    comparison_available: Optional[bool] = False
    dynamics: Optional[str] = None
    # comment: Optional[str] = None


class ContrastMammographyRCFindingCreate(ContrastMammographyRCFindingBase):
    contrast_mammo_id: int


class ContrastMammographyRCFinding(ContrastMammographyRCFindingBase):
    id: int
    contrast_mammo_id: int

    class Config:
        from_attributes = True


# Contrast Mammography Schemas
class ContrastMammographyBase(BaseModel):
    exam_date: date
    study_stage: Optional[int] = None
    menstrual_cycle_day: Optional[str] = None
    birads_category_left: Optional[str] = None
    birads_category_right: Optional[str] = None
    acr_density_left: Optional[str] = None
    acr_density_right: Optional[str] = None
    bpe_level: Optional[str] = None
    bpe_symmetry: Optional[str] = None


class ContrastMammographyCreate(ContrastMammographyBase):
    patient_id: str


class ContrastMammography(ContrastMammographyBase):
    id: int
    patient_id: str
    le_findings: List[ContrastMammographyLEFinding] = []
    rc_findings: List[ContrastMammographyRCFinding] = []

    class Config:
        from_attributes = True


# Ultrasound Finding Schemas
class UltrasoundFindingBase(BaseModel):
    finding_number: Optional[int] = None
    side: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    finding_type: Optional[str] = None
    mass_shape: Optional[str] = None
    spatial_orientation: Optional[str] = None
    mass_margin: Optional[str] = None
    mass_boundary: Optional[str] = None
    echogenicity: Optional[str] = None
    structure: Optional[str] = None
    acoustic_effects: Optional[str] = None
    vascularization_type: Optional[str] = None
    surrounding_tissue: Optional[str] = None
    size_x_mm: Optional[int] = None
    size_y_mm: Optional[int] = None
    size_z_mm: Optional[int] = None
    volume_mm3: Optional[int] = None
    size_max_mm: Optional[int] = None
    size_min_mm: Optional[int] = None
    associated_feature_type: Optional[str] = None


class UltrasoundFindingCreate(UltrasoundFindingBase):
    ultrasound_id: int


class UltrasoundFinding(UltrasoundFindingBase):
    id: int
    ultrasound_id: int

    class Config:
        from_attributes = True


# Ultrasound Lymph Node Schemas
class UltrasoundLymphNodeBase(BaseModel):
    finding_number: Optional[int] = None
    side: Optional[str] = None
    has_changes: Optional[str] = None
    lymph_node_group: Optional[str] = None
    shape: Optional[str] = None
    margin: Optional[str] = None
    boundary: Optional[str] = None
    size_x_mm: Optional[int] = None
    size_y_mm: Optional[int] = None
    size_z_mm: Optional[int] = None
    medulla_echogenicity: Optional[str] = None
    cortex_echogenicity: Optional[str] = None
    has_widened_cortex: Optional[str] = None
    vascularization_type: Optional[str] = None
    hyperplasia_type: Optional[str] = None


class UltrasoundLymphNodeCreate(UltrasoundLymphNodeBase):
    ultrasound_id: int


class UltrasoundLymphNode(UltrasoundLymphNodeBase):
    id: int
    ultrasound_id: int

    class Config:
        from_attributes = True


# Ultrasound Schemas
class UltrasoundBase(BaseModel):
    exam_date: date
    study_stage: Optional[int] = None
    menstrual_cycle_day: Optional[str] = None
    patient_position: Optional[str] = None
    birads_right: Optional[str] = None
    birads_left: Optional[str] = None
    acr_density_right: Optional[str] = None
    acr_density_left: Optional[str] = None
    comparison_available: Optional[bool] = False
    dynamics: Optional[str] = None
    comment: Optional[str] = None


class UltrasoundCreate(UltrasoundBase):
    patient_id: str


class Ultrasound(UltrasoundBase):
    id: int
    patient_id: str
    findings: List[UltrasoundFinding] = []
    lymph_nodes: List[UltrasoundLymphNode] = []

    class Config:
        from_attributes = True


# MRT Finding Schemas
class MRTFindingBase(BaseModel):
    finding_number: Optional[int] = None
    side: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    finding_type: Optional[str] = None
    mass_shape: Optional[str] = None
    mass_margin: Optional[str] = None
    size_x_mm: Optional[int] = None
    size_y_mm: Optional[int] = None
    size_z_mm: Optional[int] = None
    volume_mm3: Optional[int] = None
    size_max_mm: Optional[int] = None
    size_min_mm: Optional[int] = None
    t2_signal: Optional[str] = None
    enhancement_characteristics: Optional[str] = None
    kinetics: Optional[str] = None
    dwi_signal: Optional[str] = None
    adc_signal: Optional[str] = None
    adc_value: Optional[float] = None
    invasion_signs: Optional[str] = None
    nme_distribution: Optional[str] = None
    nme_enhancement: Optional[str] = None


class MRTFindingCreate(MRTFindingBase):
    mrt_id: int


class MRTFinding(MRTFindingBase):
    id: int
    mrt_id: int

    class Config:
        from_attributes = True


# MRT Lymph Node Schemas
class MRTLymphNodeBase(BaseModel):
    finding_number: Optional[int] = None
    side: Optional[str] = None
    has_changes: Optional[str] = None
    lymph_node_group: Optional[str] = None
    shape: Optional[str] = None
    contour: Optional[str] = None
    size_cortical_mm: Optional[int] = None
    structure: Optional[str] = None
    enhancement_intensity: Optional[str] = None
    kinetics: Optional[str] = None
    dwi_signal: Optional[str] = None
    adc_signal: Optional[str] = None
    adc_value: Optional[float] = None


class MRTLymphNodeCreate(MRTLymphNodeBase):
    mrt_id: int


class MRTLymphNode(MRTLymphNodeBase):
    id: int
    mrt_id: int

    class Config:
        from_attributes = True


# MRT Schemas (обновленные)
class MRTBase(BaseModel):
    exam_date: date
    study_stage: Optional[int] = None
    menstrual_cycle_day: Optional[str] = None
    birads_right: Optional[str] = None
    birads_left: Optional[str] = None
    acr_density_right: Optional[str] = None
    acr_density_left: Optional[str] = None
    bpe_level: Optional[str] = None
    bpe_symmetry: Optional[str] = None
    comparison_available: Optional[bool] = False
    dynamics: Optional[str] = None
    comment: Optional[str] = None


class MRTCreate(MRTBase):
    patient_id: str


class MRT(MRTBase):
    id: int
    patient_id: str
    findings: List[MRTFinding] = []
    lymph_nodes: List[MRTLymphNode] = []

    class Config:
        from_attributes = True


# Histology Biopsy Finding Schemas
class HistologyBiopsyFindingBase(BaseModel):
    finding_number: Optional[int] = None
    finding_location: Optional[str] = None  # "Молочная железа" или "Лимфатический узел"
    affected_side: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    lymph_node_group: Optional[str] = None  # только для "Лимфатический узел"

    # Морфологическое заключение
    morphological_conclusion: Optional[str] = None

    # Классификация опухоли МЖ ВОЗ 2019
    who_classification: Optional[str] = None

    # Гистологическая степень злокачественности
    malignancy_degree: Optional[str] = None

    # Заключение по ИГХ
    ihc_conclusion: Optional[str] = None

    # ИГХ маркеры
    er_value: Optional[str] = None
    pr_value: Optional[str] = None
    her2_value: Optional[str] = None
    ki67_value: Optional[str] = None


class HistologyBiopsyFindingCreate(HistologyBiopsyFindingBase):
    histology_biopsy_id: int


class HistologyBiopsyFinding(HistologyBiopsyFindingBase):
    id: int
    histology_biopsy_id: int

    class Config:
        from_attributes = True


# Cytology Biopsy Finding Schemas
class CytologyBiopsyFindingBase(BaseModel):
    finding_number: Optional[int] = None
    affected_side: Optional[str] = None
    cytology_body_part: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    lymph_node_group: Optional[str] = None
    diagnostic_category: Optional[str] = None
    cytology_report: Optional[str] = None


class CytologyBiopsyFindingCreate(CytologyBiopsyFindingBase):
    cytology_biopsy_id: int


class CytologyBiopsyFinding(CytologyBiopsyFindingBase):
    id: int
    cytology_biopsy_id: int

    class Config:
        from_attributes = True


# Histology Biopsy Schemas (ОБНОВЛЕННЫЕ)
class HistologyBiopsyBase(BaseModel):
    exam_date: date


class HistologyBiopsyCreate(HistologyBiopsyBase):
    patient_id: str


class HistologyBiopsy(HistologyBiopsyBase):
    id: int
    patient_id: str
    findings: List[HistologyBiopsyFinding] = []

    class Config:
        from_attributes = True


# Cytology Biopsy Schemas (ОБНОВЛЕННЫЕ)
class CytologyBiopsyBase(BaseModel):
    exam_date: date


class CytologyBiopsyCreate(CytologyBiopsyBase):
    patient_id: str


class CytologyBiopsy(CytologyBiopsyBase):
    id: int
    patient_id: str
    findings: List[CytologyBiopsyFinding] = []

    class Config:
        from_attributes = True


# Histology Postop Finding Schemas
class HistologyPostopFindingBase(BaseModel):
    finding_number: Optional[int] = None
    finding_location: Optional[str] = None
    affected_side: Optional[str] = None
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    lymph_node_group: Optional[str] = None
    morphological_conclusion: Optional[str] = None
    who_classification: Optional[str] = None
    malignancy_degree: Optional[str] = None
    ihc_conclusion: Optional[str] = None
    er_value: Optional[str] = None
    pr_value: Optional[str] = None
    her2_value: Optional[str] = None
    ki67_value: Optional[str] = None
    size_1_mm: Optional[int] = None
    size_2_mm: Optional[int] = None
    size_3_mm: Optional[int] = None
    volume_mm3: Optional[int] = None
    size_max_mm: Optional[int] = None
    size_min_mm: Optional[int] = None


class HistologyPostopFindingCreate(HistologyPostopFindingBase):
    histology_postop_id: int


class HistologyPostopFinding(HistologyPostopFindingBase):
    id: int
    histology_postop_id: int

    class Config:
        from_attributes = True

class HistologyPostopBase(BaseModel):
    exam_date: date


class HistologyPostopCreate(HistologyPostopBase):
    patient_id: str


class HistologyPostop(HistologyPostopBase):
    id: int
    patient_id: str
    findings: List[HistologyPostopFinding] = []

    class Config:
        from_attributes = True

class PatientWithData(Patient):
    mammographies: List[Mammography] = []
    contrast_mammographies: List[ContrastMammography] = []
    ultrasounds: List[Ultrasound] = []
    mrts: List[MRT] = []
    histology_biopsies: List[HistologyBiopsy] = []
    cytology_biopsies: List[CytologyBiopsy] = []
    histology_postops: List[HistologyPostop] = []  # Убедитесь, что это уже есть