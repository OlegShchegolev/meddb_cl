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
    quadrant_location: Optional[str] = None
    depth_location: Optional[str] = None
    finding_type: Optional[str] = None
    mass_shape: Optional[str] = None
    mass_margin: Optional[str] = None
    mass_density: Optional[str] = None
    asymmetry_type: Optional[str] = None
    calcification_malignancy: Optional[str] = None
    calcification_morphology: Optional[str] = None
    calcification_distribution: Optional[str] = None
    associated_feature: Optional[str] = None
    size_mm: Optional[str] = None


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
    affected_side: Optional[str] = None
    birads_category: Optional[str] = None
    acr_density: Optional[str] = None
    comparison_available: Optional[bool] = False
    dynamics: Optional[str] = None
    comment: Optional[str] = None


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


# Contrast Mammography Schemas
class ContrastMammographyBase(BaseModel):
    exam_date: date
    findings: Optional[str] = None
    comment: Optional[str] = None


class ContrastMammographyCreate(ContrastMammographyBase):
    patient_id: str


class ContrastMammography(ContrastMammographyBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# Ultrasound Schemas
class UltrasoundBase(BaseModel):
    exam_date: date
    findings: Optional[str] = None
    comment: Optional[str] = None


class UltrasoundCreate(UltrasoundBase):
    patient_id: str


class Ultrasound(UltrasoundBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# MRT Schemas
class MRTBase(BaseModel):
    exam_date: date
    findings: Optional[str] = None
    comment: Optional[str] = None


class MRTCreate(MRTBase):
    patient_id: str


class MRT(MRTBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# Histology Biopsy Schemas
class HistologyBiopsyBase(BaseModel):
    exam_date: date
    findings: Optional[str] = None
    ihc_results: Optional[str] = None
    comment: Optional[str] = None


class HistologyBiopsyCreate(HistologyBiopsyBase):
    patient_id: str


class HistologyBiopsy(HistologyBiopsyBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# Cytology Biopsy Schemas
class CytologyBiopsyBase(BaseModel):
    exam_date: date
    findings: Optional[str] = None
    comment: Optional[str] = None


class CytologyBiopsyCreate(CytologyBiopsyBase):
    patient_id: str


class CytologyBiopsy(CytologyBiopsyBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# Histology Postop Schemas
class HistologyPostopBase(BaseModel):
    exam_date: date
    findings: Optional[str] = None
    ihc_results: Optional[str] = None
    comment: Optional[str] = None


class HistologyPostopCreate(HistologyPostopBase):
    patient_id: str


class HistologyPostop(HistologyPostopBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# Combined Patient Schema
class PatientWithData(Patient):
    mammographies: List[Mammography] = []
    contrast_mammographies: List[ContrastMammography] = []
    ultrasounds: List[Ultrasound] = []
    mrts: List[MRT] = []
    histology_biopsies: List[HistologyBiopsy] = []
    cytology_biopsies: List[CytologyBiopsy] = []
    histology_postops: List[HistologyPostop] = []