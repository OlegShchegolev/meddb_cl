from pydantic import BaseModel
from datetime import date
from typing import Optional, List


# Patient Schemas
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class PatientCreate(BaseModel):
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class PatientUpdate(PatientBase):
    pass


class Patient(PatientBase):
    id: str

    class Config:
        from_attributes = True


# Mammography Schemas
class MammographyBase(BaseModel):
    exam_date: date
    breast_density: Optional[str] = None
    findings: Optional[str] = None
    birads_score: Optional[int] = None
    notes: Optional[str] = None


class MammographyCreate(MammographyBase):
    patient_id: str


class MammographyUpdate(MammographyBase):
    patient_id: str


class Mammography(MammographyBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# Ultrasound Schemas
class UltrasoundBase(BaseModel):
    exam_date: date
    organ: Optional[str] = None
    findings: Optional[str] = None
    measurements: Optional[str] = None
    notes: Optional[str] = None


class UltrasoundCreate(UltrasoundBase):
    patient_id: str


class UltrasoundUpdate(UltrasoundBase):
    patient_id: str


class Ultrasound(UltrasoundBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# MRT Schemas
class MRTBase(BaseModel):
    exam_date: date
    body_part: Optional[str] = None
    contrast_used: Optional[str] = None
    findings: Optional[str] = None
    impression: Optional[str] = None
    notes: Optional[str] = None


class MRTCreate(MRTBase):
    patient_id: str


class MRTUpdate(MRTBase):
    patient_id: str


class MRT(MRTBase):
    id: int
    patient_id: str

    class Config:
        from_attributes = True


# Combined schemas
class PatientWithData(Patient):
    mammographies: List[Mammography] = []
    ultrasounds: List[Ultrasound] = []
    mrts: List[MRT] = []