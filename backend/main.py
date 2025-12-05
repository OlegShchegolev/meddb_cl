from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import pandas as pd
import io

import database
import schemas

app = FastAPI(title="Medical Data Management API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    database.init_db()


# Patient endpoints
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(database.get_db)):
    # Check if patient ID already exists
    existing_patient = db.query(database.Patient).filter(database.Patient.id == patient.id).first()
    if existing_patient:
        raise HTTPException(status_code=400, detail="Patient ID already exists")

    db_patient = database.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/patients/", response_model=List[schemas.Patient])
def get_patients(
        skip: int = 0,
        limit: int = 100,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        db: Session = Depends(database.get_db)
):
    query = db.query(database.Patient)
    if first_name:
        query = query.filter(database.Patient.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(database.Patient.last_name.ilike(f"%{last_name}%"))
    return query.offset(skip).limit(limit).all()


@app.get("/patients/{patient_id}", response_model=schemas.PatientWithData)
def get_patient(patient_id: str, db: Session = Depends(database.get_db)):
    patient = db.query(database.Patient).filter(database.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.put("/patients/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: str, patient: schemas.PatientUpdate, db: Session = Depends(database.get_db)):
    db_patient = db.query(database.Patient).filter(database.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in patient.dict().items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(database.get_db)):
    db_patient = db.query(database.Patient).filter(database.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(db_patient)
    db.commit()
    return {"message": "Patient deleted successfully"}


# Mammography endpoints
@app.post("/mammographies/", response_model=schemas.Mammography)
def create_mammography(mammo: schemas.MammographyCreate, db: Session = Depends(database.get_db)):
    db_mammo = database.Mammography(**mammo.dict())
    db.add(db_mammo)
    db.commit()
    db.refresh(db_mammo)
    return db_mammo


@app.get("/mammographies/", response_model=List[schemas.Mammography])
def get_mammographies(
        patient_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        db: Session = Depends(database.get_db)
):
    query = db.query(database.Mammography)
    if patient_id:
        query = query.filter(database.Mammography.patient_id == patient_id)
    if date_from:
        query = query.filter(database.Mammography.exam_date >= date_from)
    if date_to:
        query = query.filter(database.Mammography.exam_date <= date_to)
    return query.all()


@app.get("/mammographies/{mammo_id}", response_model=schemas.Mammography)
def get_mammography(mammo_id: int, db: Session = Depends(database.get_db)):
    mammo = db.query(database.Mammography).filter(database.Mammography.id == mammo_id).first()
    if not mammo:
        raise HTTPException(status_code=404, detail="Mammography not found")
    return mammo


@app.put("/mammographies/{mammo_id}", response_model=schemas.Mammography)
def update_mammography(mammo_id: int, mammo: schemas.MammographyUpdate, db: Session = Depends(database.get_db)):
    db_mammo = db.query(database.Mammography).filter(database.Mammography.id == mammo_id).first()
    if not db_mammo:
        raise HTTPException(status_code=404, detail="Mammography not found")
    for key, value in mammo.dict().items():
        setattr(db_mammo, key, value)
    db.commit()
    db.refresh(db_mammo)
    return db_mammo


@app.delete("/mammographies/{mammo_id}")
def delete_mammography(mammo_id: int, db: Session = Depends(database.get_db)):
    db_mammo = db.query(database.Mammography).filter(database.Mammography.id == mammo_id).first()
    if not db_mammo:
        raise HTTPException(status_code=404, detail="Mammography not found")
    db.delete(db_mammo)
    db.commit()
    return {"message": "Mammography deleted successfully"}


# Ultrasound endpoints
@app.post("/ultrasounds/", response_model=schemas.Ultrasound)
def create_ultrasound(us: schemas.UltrasoundCreate, db: Session = Depends(database.get_db)):
    db_us = database.Ultrasound(**us.dict())
    db.add(db_us)
    db.commit()
    db.refresh(db_us)
    return db_us


@app.get("/ultrasounds/", response_model=List[schemas.Ultrasound])
def get_ultrasounds(
        patient_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        organ: Optional[str] = None,
        db: Session = Depends(database.get_db)
):
    query = db.query(database.Ultrasound)
    if patient_id:
        query = query.filter(database.Ultrasound.patient_id == patient_id)
    if date_from:
        query = query.filter(database.Ultrasound.exam_date >= date_from)
    if date_to:
        query = query.filter(database.Ultrasound.exam_date <= date_to)
    if organ:
        query = query.filter(database.Ultrasound.organ.ilike(f"%{organ}%"))
    return query.all()


@app.get("/ultrasounds/{us_id}", response_model=schemas.Ultrasound)
def get_ultrasound(us_id: int, db: Session = Depends(database.get_db)):
    us = db.query(database.Ultrasound).filter(database.Ultrasound.id == us_id).first()
    if not us:
        raise HTTPException(status_code=404, detail="Ultrasound not found")
    return us


@app.put("/ultrasounds/{us_id}", response_model=schemas.Ultrasound)
def update_ultrasound(us_id: int, us: schemas.UltrasoundUpdate, db: Session = Depends(database.get_db)):
    db_us = db.query(database.Ultrasound).filter(database.Ultrasound.id == us_id).first()
    if not db_us:
        raise HTTPException(status_code=404, detail="Ultrasound not found")
    for key, value in us.dict().items():
        setattr(db_us, key, value)
    db.commit()
    db.refresh(db_us)
    return db_us


@app.delete("/ultrasounds/{us_id}")
def delete_ultrasound(us_id: int, db: Session = Depends(database.get_db)):
    db_us = db.query(database.Ultrasound).filter(database.Ultrasound.id == us_id).first()
    if not db_us:
        raise HTTPException(status_code=404, detail="Ultrasound not found")
    db.delete(db_us)
    db.commit()
    return {"message": "Ultrasound deleted successfully"}


# MRT endpoints
@app.post("/mrts/", response_model=schemas.MRT)
def create_mrt(mrt: schemas.MRTCreate, db: Session = Depends(database.get_db)):
    db_mrt = database.MRT(**mrt.dict())
    db.add(db_mrt)
    db.commit()
    db.refresh(db_mrt)
    return db_mrt


@app.get("/mrts/", response_model=List[schemas.MRT])
def get_mrts(
        patient_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        body_part: Optional[str] = None,
        db: Session = Depends(database.get_db)
):
    query = db.query(database.MRT)
    if patient_id:
        query = query.filter(database.MRT.patient_id == patient_id)
    if date_from:
        query = query.filter(database.MRT.exam_date >= date_from)
    if date_to:
        query = query.filter(database.MRT.exam_date <= date_to)
    if body_part:
        query = query.filter(database.MRT.body_part.ilike(f"%{body_part}%"))
    return query.all()


@app.get("/mrts/{mrt_id}", response_model=schemas.MRT)
def get_mrt(mrt_id: int, db: Session = Depends(database.get_db)):
    mrt = db.query(database.MRT).filter(database.MRT.id == mrt_id).first()
    if not mrt:
        raise HTTPException(status_code=404, detail="MRT not found")
    return mrt


@app.put("/mrts/{mrt_id}", response_model=schemas.MRT)
def update_mrt(mrt_id: int, mrt: schemas.MRTUpdate, db: Session = Depends(database.get_db)):
    db_mrt = db.query(database.MRT).filter(database.MRT.id == mrt_id).first()
    if not db_mrt:
        raise HTTPException(status_code=404, detail="MRT not found")
    for key, value in mrt.dict().items():
        setattr(db_mrt, key, value)
    db.commit()
    db.refresh(db_mrt)
    return db_mrt


@app.delete("/mrts/{mrt_id}")
def delete_mrt(mrt_id: int, db: Session = Depends(database.get_db)):
    db_mrt = db.query(database.MRT).filter(database.MRT.id == mrt_id).first()
    if not db_mrt:
        raise HTTPException(status_code=404, detail="MRT not found")
    db.delete(db_mrt)
    db.commit()
    return {"message": "MRT deleted successfully"}


# Export endpoint
@app.get("/export/{table_name}")
def export_data(
        table_name: str,
        patient_id: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        db: Session = Depends(database.get_db)
):
    if table_name == "patients":
        query = db.query(database.Patient)
        if patient_id:
            query = query.filter(database.Patient.id == patient_id)
        data = [
            {
                "id": p.id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "date_of_birth": str(p.date_of_birth),
                "gender": p.gender,
                "email": p.email,
                "phone": p.phone,
                "address": p.address
            }
            for p in query.all()
        ]
    elif table_name == "mammographies":
        query = db.query(database.Mammography).join(database.Patient)
        if patient_id:
            query = query.filter(database.Mammography.patient_id == patient_id)
        if date_from:
            query = query.filter(database.Mammography.exam_date >= date_from)
        if date_to:
            query = query.filter(database.Mammography.exam_date <= date_to)
        data = [
            {
                "mammography_id": m.id,
                "patient_id": m.patient_id,
                "patient_first_name": m.patient.first_name,
                "patient_last_name": m.patient.last_name,
                "patient_date_of_birth": str(m.patient.date_of_birth),
                "patient_gender": m.patient.gender,
                "patient_email": m.patient.email,
                "patient_phone": m.patient.phone,
                "exam_date": str(m.exam_date),
                "breast_density": m.breast_density,
                "findings": m.findings,
                "birads_score": m.birads_score,
                "notes": m.notes
            }
            for m in query.all()
        ]
    elif table_name == "ultrasounds":
        query = db.query(database.Ultrasound).join(database.Patient)
        if patient_id:
            query = query.filter(database.Ultrasound.patient_id == patient_id)
        if date_from:
            query = query.filter(database.Ultrasound.exam_date >= date_from)
        if date_to:
            query = query.filter(database.Ultrasound.exam_date <= date_to)
        data = [
            {
                "ultrasound_id": u.id,
                "patient_id": u.patient_id,
                "patient_first_name": u.patient.first_name,
                "patient_last_name": u.patient.last_name,
                "patient_date_of_birth": str(u.patient.date_of_birth),
                "patient_gender": u.patient.gender,
                "patient_email": u.patient.email,
                "patient_phone": u.patient.phone,
                "exam_date": str(u.exam_date),
                "organ": u.organ,
                "findings": u.findings,
                "measurements": u.measurements,
                "notes": u.notes
            }
            for u in query.all()
        ]
    elif table_name == "mrts":
        query = db.query(database.MRT).join(database.Patient)
        if patient_id:
            query = query.filter(database.MRT.patient_id == patient_id)
        if date_from:
            query = query.filter(database.MRT.exam_date >= date_from)
        if date_to:
            query = query.filter(database.MRT.exam_date <= date_to)
        data = [
            {
                "mrt_id": m.id,
                "patient_id": m.patient_id,
                "patient_first_name": m.patient.first_name,
                "patient_last_name": m.patient.last_name,
                "patient_date_of_birth": str(m.patient.date_of_birth),
                "patient_gender": m.patient.gender,
                "patient_email": m.patient.email,
                "patient_phone": m.patient.phone,
                "exam_date": str(m.exam_date),
                "body_part": m.body_part,
                "contrast_used": m.contrast_used,
                "findings": m.findings,
                "impression": m.impression,
                "notes": m.notes
            }
            for m in query.all()
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid table name")

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=table_name)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={table_name}.xlsx"}
    )