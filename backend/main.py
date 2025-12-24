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

# ==================== PATIENT ENDPOINTS ====================
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(database.get_db)):
    existing = db.query(database.Patient).filter(database.Patient.id == patient.id).first()
    if existing:
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
    last_name: Optional[str] = None,
    first_name: Optional[str] = None,
    snils: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(database.Patient)
    if last_name:
        query = query.filter(database.Patient.last_name.ilike(f"%{last_name}%"))
    if first_name:
        query = query.filter(database.Patient.first_name.ilike(f"%{first_name}%"))
    if snils:
        query = query.filter(database.Patient.snils.ilike(f"%{snils}%"))
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
    return {"message": "Patient deleted"}

# ==================== MAMMOGRAPHY ENDPOINTS ====================
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
    return {"message": "Mammography deleted"}

# ==================== MAMMOGRAPHY FINDING ENDPOINTS ====================
# @app.post("/mammography-findings/", response_model=schemas.MammographyFinding)
# def create_finding(finding: schemas.MammographyFindingCreate, db: Session = Depends(database.get_db)):
#     db_finding = database.MammographyFinding(**finding.dict())
#     db.add(db_finding)
#     db.commit()
#     db.refresh(db_finding)
#     return db_finding

@app.get("/mammography-findings/{mammo_id}", response_model=List[schemas.MammographyFinding])
def get_findings(mammo_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.MammographyFinding).filter(database.MammographyFinding.mammography_id == mammo_id).all()

# @app.put("/mammography-findings/{finding_id}", response_model=schemas.MammographyFinding)
# def update_finding(finding_id: int, finding: schemas.MammographyFindingCreate, db: Session = Depends(database.get_db)):
#     db_finding = db.query(database.MammographyFinding).filter(database.MammographyFinding.id == finding_id).first()
#     if not db_finding:
#         raise HTTPException(status_code=404, detail="Finding not found")
#     for key, value in finding.dict().items():
#         setattr(db_finding, key, value)
#     db.commit()
#     db.refresh(db_finding)
#     return db_finding

# @app.delete("/mammography-findings/{finding_id}")
# def delete_finding(finding_id: int, db: Session = Depends(database.get_db)):
#     db_finding = db.query(database.MammographyFinding).filter(database.MammographyFinding.id == finding_id).first()
#     if not db_finding:
#         raise HTTPException(status_code=404, detail="Finding not found")
#     db.delete(db_finding)
#     db.commit()
#     return {"message": "Finding deleted"}

# ==================== CONTRAST MAMMOGRAPHY ENDPOINTS ====================
@app.post("/contrast-mammographies/", response_model=schemas.ContrastMammography)
def create_contrast_mammo(item: schemas.ContrastMammographyCreate, db: Session = Depends(database.get_db)):
    db_item = database.ContrastMammography(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/contrast-mammographies/", response_model=List[schemas.ContrastMammography])
def get_contrast_mammos(
    patient_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(database.get_db)
):
    query = db.query(database.ContrastMammography)
    if patient_id:
        query = query.filter(database.ContrastMammography.patient_id == patient_id)
    if date_from:
        query = query.filter(database.ContrastMammography.exam_date >= date_from)
    if date_to:
        query = query.filter(database.ContrastMammography.exam_date <= date_to)
    return query.all()

@app.get("/contrast-mammographies/{item_id}", response_model=schemas.ContrastMammography)
def get_contrast_mammo(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.ContrastMammography).filter(database.ContrastMammography.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    return item

@app.put("/contrast-mammographies/{item_id}", response_model=schemas.ContrastMammography)
def update_contrast_mammo(item_id: int, item: schemas.ContrastMammographyCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(database.ContrastMammography).filter(database.ContrastMammography.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/contrast-mammographies/{item_id}")
def delete_contrast_mammo(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.ContrastMammography).filter(database.ContrastMammography.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(item)
    db.commit()
    return {"message": "Record deleted"}

# ==================== CONTRAST MAMMOGRAPHY LE FINDING ENDPOINTS ====================
# @app.post("/contrast-mammo-le-findings/", response_model=schemas.ContrastMammographyLEFinding)
# def create_le_finding(finding: schemas.ContrastMammographyLEFindingCreate, db: Session = Depends(database.get_db)):
#     db_finding = database.ContrastMammographyLEFinding(**finding.dict())
#     db.add(db_finding)
#     db.commit()
#     db.refresh(db_finding)
#     return db_finding

@app.get("/contrast-mammo-le-findings/{mammo_id}", response_model=List[schemas.ContrastMammographyLEFinding])
def get_le_findings(mammo_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.ContrastMammographyLEFinding).filter(
        database.ContrastMammographyLEFinding.contrast_mammo_id == mammo_id
    ).all()

# @app.put("/contrast-mammo-le-findings/{finding_id}", response_model=schemas.ContrastMammographyLEFinding)
# def update_le_finding(finding_id: int, finding: schemas.ContrastMammographyLEFindingCreate, db: Session = Depends(database.get_db)):
#     db_finding = db.query(database.ContrastMammographyLEFinding).filter(
#         database.ContrastMammographyLEFinding.id == finding_id
#     ).first()
#     if not db_finding:
#         raise HTTPException(status_code=404, detail="Finding not found")
#     for key, value in finding.dict().items():
#         setattr(db_finding, key, value)
#     db.commit()
#     db.refresh(db_finding)
#     return db_finding

# @app.delete("/contrast-mammo-le-findings/{finding_id}")
# def delete_le_finding(finding_id: int, db: Session = Depends(database.get_db)):
#     finding = db.query(database.ContrastMammographyLEFinding).filter(
#         database.ContrastMammographyLEFinding.id == finding_id
#     ).first()
#     if not finding:
#         raise HTTPException(status_code=404, detail="Finding not found")
#     db.delete(finding)
#     db.commit()
#     return {"message": "Finding deleted"}

# ==================== CONTRAST MAMMOGRAPHY RC FINDING ENDPOINTS ====================
# @app.post("/contrast-mammo-rc-findings/", response_model=schemas.ContrastMammographyRCFinding)
# def create_rc_finding(finding: schemas.ContrastMammographyRCFindingCreate, db: Session = Depends(database.get_db)):
#     db_finding = database.ContrastMammographyRCFinding(**finding.dict())
#     db.add(db_finding)
#     db.commit()
#     db.refresh(db_finding)
#     return db_finding

@app.get("/contrast-mammo-rc-findings/{mammo_id}", response_model=List[schemas.ContrastMammographyRCFinding])
def get_rc_findings(mammo_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.ContrastMammographyRCFinding).filter(
        database.ContrastMammographyRCFinding.contrast_mammo_id == mammo_id
    ).all()

# @app.put("/contrast-mammo-rc-findings/{finding_id}", response_model=schemas.ContrastMammographyRCFinding)
# def update_rc_finding(finding_id: int, finding: schemas.ContrastMammographyRCFindingCreate, db: Session = Depends(database.get_db)):
#     db_finding = db.query(database.ContrastMammographyRCFinding).filter(
#         database.ContrastMammographyRCFinding.id == finding_id
#     ).first()
#     if not db_finding:
#         raise HTTPException(status_code=404, detail="Finding not found")
#     for key, value in finding.dict().items():
#         setattr(db_finding, key, value)
#     db.commit()
#     db.refresh(db_finding)
#     return db_finding

# @app.delete("/contrast-mammo-rc-findings/{finding_id}")
# def delete_rc_finding(finding_id: int, db: Session = Depends(database.get_db)):
#     finding = db.query(database.ContrastMammographyRCFinding).filter(
#         database.ContrastMammographyRCFinding.id == finding_id
#     ).first()
#     if not finding:
#         raise HTTPException(status_code=404, detail="Finding not found")
#     db.delete(finding)
#     db.commit()
#     return {"message": "Finding deleted"}

# ==================== ULTRASOUND ENDPOINTS ====================
@app.post("/ultrasounds/", response_model=schemas.Ultrasound)
def create_ultrasound(item: schemas.UltrasoundCreate, db: Session = Depends(database.get_db)):
    db_item = database.Ultrasound(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/ultrasounds/", response_model=List[schemas.Ultrasound])
def get_ultrasounds(patient_id: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(database.Ultrasound)
    if patient_id:
        query = query.filter(database.Ultrasound.patient_id == patient_id)
    return query.all()

@app.put("/ultrasounds/{item_id}", response_model=schemas.Ultrasound)
def update_ultrasound(item_id: int, item: schemas.UltrasoundCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(database.Ultrasound).filter(database.Ultrasound.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/ultrasounds/{item_id}")
def delete_ultrasound(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.Ultrasound).filter(database.Ultrasound.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(item)
    db.commit()
    return {"message": "Record deleted"}

# Замените существующие MRT эндпоинты на следующие:

@app.post("/mrts/", response_model=schemas.MRT)
def create_mrt(item: schemas.MRTCreate, db: Session = Depends(database.get_db)):
    db_item = database.MRT(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/mrts/", response_model=List[schemas.MRT])
def get_mrts(patient_id: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(database.MRT)
    if patient_id:
        query = query.filter(database.MRT.patient_id == patient_id)
    return query.all()


@app.get("/mrts/{item_id}", response_model=schemas.MRT)
def get_mrt(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.MRT).filter(database.MRT.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    return item


@app.put("/mrts/{item_id}", response_model=schemas.MRT)
def update_mrt(item_id: int, item: schemas.MRTCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(database.MRT).filter(database.MRT.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/mrts/{item_id}")
def delete_mrt(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.MRT).filter(database.MRT.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(item)
    db.commit()
    return {"message": "Record deleted"}


# ==================== MRT FINDING ENDPOINTS ====================
@app.post("/mrt-findings/", response_model=schemas.MRTFinding)
def create_mrt_finding(finding: schemas.MRTFindingCreate, db: Session = Depends(database.get_db)):
    next_number = get_next_finding_number(
        db, database.MRTFinding, "mrt_id", finding.mrt_id
    )

    finding_data = finding.dict()
    finding_data['finding_number'] = next_number

    db_finding = database.MRTFinding(**finding_data)
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.get("/mrt-findings/{mrt_id}", response_model=List[schemas.MRTFinding])
def get_mrt_findings(mrt_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.MRTFinding).filter(
        database.MRTFinding.mrt_id == mrt_id
    ).all()


@app.put("/mrt-findings/{finding_id}", response_model=schemas.MRTFinding)
def update_mrt_finding(finding_id: int, finding: schemas.MRTFindingCreate,
                       db: Session = Depends(database.get_db)):
    db_finding = db.query(database.MRTFinding).filter(
        database.MRTFinding.id == finding_id
    ).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    old_mrt_id = db_finding.mrt_id
    new_mrt_id = finding.mrt_id

    for key, value in finding.dict().items():
        setattr(db_finding, key, value)

    if old_mrt_id != new_mrt_id:
        next_number = get_next_finding_number(
            db, database.MRTFinding, "mrt_id", new_mrt_id
        )
        db_finding.finding_number = next_number

    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.delete("/mrt-findings/{finding_id}")
def delete_mrt_finding(finding_id: int, db: Session = Depends(database.get_db)):
    finding = db.query(database.MRTFinding).filter(
        database.MRTFinding.id == finding_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    mrt_id = finding.mrt_id
    db.delete(finding)
    db.commit()

    renumber_findings(
        db, database.MRTFinding, "mrt_id", mrt_id
    )

    return {"message": "Finding deleted and numbers reordered"}


# ==================== MRT LYMPH NODE ENDPOINTS ====================
@app.post("/mrt-lymph-nodes/", response_model=schemas.MRTLymphNode)
def create_mrt_lymph_node(lymph_node: schemas.MRTLymphNodeCreate,
                          db: Session = Depends(database.get_db)):
    next_number = get_next_finding_number(
        db, database.MRTLymphNode, "mrt_id", lymph_node.mrt_id
    )

    lymph_node_data = lymph_node.dict()
    lymph_node_data['finding_number'] = next_number

    db_lymph_node = database.MRTLymphNode(**lymph_node_data)
    db.add(db_lymph_node)
    db.commit()
    db.refresh(db_lymph_node)
    return db_lymph_node


@app.get("/mrt-lymph-nodes/{mrt_id}", response_model=List[schemas.MRTLymphNode])
def get_mrt_lymph_nodes(mrt_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.MRTLymphNode).filter(
        database.MRTLymphNode.mrt_id == mrt_id
    ).all()


@app.put("/mrt-lymph-nodes/{lymph_node_id}", response_model=schemas.MRTLymphNode)
def update_mrt_lymph_node(lymph_node_id: int, lymph_node: schemas.MRTLymphNodeCreate,
                          db: Session = Depends(database.get_db)):
    db_lymph_node = db.query(database.MRTLymphNode).filter(
        database.MRTLymphNode.id == lymph_node_id
    ).first()
    if not db_lymph_node:
        raise HTTPException(status_code=404, detail="Lymph node not found")

    old_mrt_id = db_lymph_node.mrt_id
    new_mrt_id = lymph_node.mrt_id

    for key, value in lymph_node.dict().items():
        setattr(db_lymph_node, key, value)

    if old_mrt_id != new_mrt_id:
        next_number = get_next_finding_number(
            db, database.MRTLymphNode, "mrt_id", new_mrt_id
        )
        db_lymph_node.finding_number = next_number

    db.commit()
    db.refresh(db_lymph_node)
    return db_lymph_node


@app.delete("/mrt-lymph-nodes/{lymph_node_id}")
def delete_mrt_lymph_node(lymph_node_id: int, db: Session = Depends(database.get_db)):
    lymph_node = db.query(database.MRTLymphNode).filter(
        database.MRTLymphNode.id == lymph_node_id
    ).first()
    if not lymph_node:
        raise HTTPException(status_code=404, detail="Lymph node not found")

    mrt_id = lymph_node.mrt_id
    db.delete(lymph_node)
    db.commit()

    renumber_findings(
        db, database.MRTLymphNode, "mrt_id", mrt_id
    )

    return {"message": "Lymph node deleted and numbers reordered"}

# ==================== HISTOLOGY BIOPSY ENDPOINTS ====================
@app.post("/histology-biopsies/", response_model=schemas.HistologyBiopsy)
def create_histology_biopsy(item: schemas.HistologyBiopsyCreate, db: Session = Depends(database.get_db)):
    db_item = database.HistologyBiopsy(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/histology-biopsies/", response_model=List[schemas.HistologyBiopsy])
def get_histology_biopsies(patient_id: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(database.HistologyBiopsy)
    if patient_id:
        query = query.filter(database.HistologyBiopsy.patient_id == patient_id)
    return query.all()

@app.put("/histology-biopsies/{item_id}", response_model=schemas.HistologyBiopsy)
def update_histology_biopsy(item_id: int, item: schemas.HistologyBiopsyCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(database.HistologyBiopsy).filter(database.HistologyBiopsy.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/histology-biopsies/{item_id}")
def delete_histology_biopsy(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.HistologyBiopsy).filter(database.HistologyBiopsy.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(item)
    db.commit()
    return {"message": "Record deleted"}

# ==================== CYTOLOGY BIOPSY ENDPOINTS ====================
@app.post("/cytology-biopsies/", response_model=schemas.CytologyBiopsy)
def create_cytology_biopsy(item: schemas.CytologyBiopsyCreate, db: Session = Depends(database.get_db)):
    db_item = database.CytologyBiopsy(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/cytology-biopsies/", response_model=List[schemas.CytologyBiopsy])
def get_cytology_biopsies(patient_id: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(database.CytologyBiopsy)
    if patient_id:
        query = query.filter(database.CytologyBiopsy.patient_id == patient_id)
    return query.all()

@app.put("/cytology-biopsies/{item_id}", response_model=schemas.CytologyBiopsy)
def update_cytology_biopsy(item_id: int, item: schemas.CytologyBiopsyCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(database.CytologyBiopsy).filter(database.CytologyBiopsy.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/cytology-biopsies/{item_id}")
def delete_cytology_biopsy(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.CytologyBiopsy).filter(database.CytologyBiopsy.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(item)
    db.commit()
    return {"message": "Record deleted"}

# ==================== HISTOLOGY POSTOP ENDPOINTS ====================
@app.post("/histology-postops/", response_model=schemas.HistologyPostop)
def create_histology_postop(item: schemas.HistologyPostopCreate, db: Session = Depends(database.get_db)):
    db_item = database.HistologyPostop(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/histology-postops/", response_model=List[schemas.HistologyPostop])
def get_histology_postops(patient_id: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(database.HistologyPostop)
    if patient_id:
        query = query.filter(database.HistologyPostop.patient_id == patient_id)
    return query.all()

@app.put("/histology-postops/{item_id}", response_model=schemas.HistologyPostop)
def update_histology_postop(item_id: int, item: schemas.HistologyPostopCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(database.HistologyPostop).filter(database.HistologyPostop.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/histology-postops/{item_id}")
def delete_histology_postop(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.HistologyPostop).filter(database.HistologyPostop.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(item)
    db.commit()
    return {"message": "Record deleted"}


# ==================== HELPER FUNCTIONS FOR FINDING NUMBERS ====================

def get_next_finding_number(db: Session, model, foreign_key_field, foreign_key_value):
    """
    Получить минимальный незанятый номер находки для указанного исследования
    """
    existing_numbers = db.query(model.finding_number).filter(
        getattr(model, foreign_key_field) == foreign_key_value
    ).all()

    existing_numbers = [n[0] for n in existing_numbers if n[0] is not None]

    # Найти минимальное отсутствующее число
    if not existing_numbers:
        return 1

    max_num = max(existing_numbers)
    all_numbers = set(range(1, max_num + 2))  # +2 чтобы включить max_num+1
    available_numbers = all_numbers - set(existing_numbers)

    return min(available_numbers)


def renumber_findings(db: Session, model, foreign_key_field, foreign_key_value):
    """
    Перенумеровать все находки исследования по порядку начиная с 1
    """
    findings = db.query(model).filter(
        getattr(model, foreign_key_field) == foreign_key_value
    ).order_by(
        model.finding_number.asc(),  # Сначала сортируем по старому номеру
        model.id.asc()  # Затем по ID для одинаковых номеров
    ).all()

    for index, finding in enumerate(findings, start=1):
        finding.finding_number = index

    db.commit()


# ==================== UPDATED MAMMOGRAPHY FINDING ENDPOINTS ====================
@app.post("/mammography-findings/", response_model=schemas.MammographyFinding)
def create_finding(finding: schemas.MammographyFindingCreate, db: Session = Depends(database.get_db)):
    # Получаем следующий доступный номер
    next_number = get_next_finding_number(
        db, database.MammographyFinding, "mammography_id", finding.mammography_id
    )

    # Создаем словарь данных и добавляем автоматический номер
    finding_data = finding.dict()
    finding_data['finding_number'] = next_number

    db_finding = database.MammographyFinding(**finding_data)
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.put("/mammography-findings/{finding_id}", response_model=schemas.MammographyFinding)
def update_finding(finding_id: int, finding: schemas.MammographyFindingCreate, db: Session = Depends(database.get_db)):
    db_finding = db.query(database.MammographyFinding).filter(database.MammographyFinding.id == finding_id).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Сохраняем старое mammography_id для проверки
    old_mammography_id = db_finding.mammography_id
    new_mammography_id = finding.mammography_id

    # Обновляем все поля
    for key, value in finding.dict().items():
        setattr(db_finding, key, value)

    # Если изменилось mammography_id, нужно получить новый номер
    if old_mammography_id != new_mammography_id:
        next_number = get_next_finding_number(
            db, database.MammographyFinding, "mammography_id", new_mammography_id
        )
        db_finding.finding_number = next_number

    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.delete("/mammography-findings/{finding_id}")
def delete_finding(finding_id: int, db: Session = Depends(database.get_db)):
    db_finding = db.query(database.MammographyFinding).filter(database.MammographyFinding.id == finding_id).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Сохраняем mammography_id для перенумерации
    mammography_id = db_finding.mammography_id

    # Удаляем находку
    db.delete(db_finding)
    db.commit()

    # Перенумеровываем оставшиеся находки
    renumber_findings(
        db, database.MammographyFinding, "mammography_id", mammography_id
    )

    return {"message": "Finding deleted and numbers reordered"}


# ==================== UPDATED CONTRAST MAMMOGRAPHY LE FINDING ENDPOINTS ====================
@app.post("/contrast-mammo-le-findings/", response_model=schemas.ContrastMammographyLEFinding)
def create_le_finding(finding: schemas.ContrastMammographyLEFindingCreate, db: Session = Depends(database.get_db)):
    next_number = get_next_finding_number(
        db, database.ContrastMammographyLEFinding, "contrast_mammo_id", finding.contrast_mammo_id
    )

    finding_data = finding.dict()
    finding_data['finding_number'] = next_number

    db_finding = database.ContrastMammographyLEFinding(**finding_data)
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.put("/contrast-mammo-le-findings/{finding_id}", response_model=schemas.ContrastMammographyLEFinding)
def update_le_finding(finding_id: int, finding: schemas.ContrastMammographyLEFindingCreate,
                      db: Session = Depends(database.get_db)):
    db_finding = db.query(database.ContrastMammographyLEFinding).filter(
        database.ContrastMammographyLEFinding.id == finding_id
    ).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    old_contrast_mammo_id = db_finding.contrast_mammo_id
    new_contrast_mammo_id = finding.contrast_mammo_id

    for key, value in finding.dict().items():
        setattr(db_finding, key, value)

    if old_contrast_mammo_id != new_contrast_mammo_id:
        next_number = get_next_finding_number(
            db, database.ContrastMammographyLEFinding, "contrast_mammo_id", new_contrast_mammo_id
        )
        db_finding.finding_number = next_number

    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.delete("/contrast-mammo-le-findings/{finding_id}")
def delete_le_finding(finding_id: int, db: Session = Depends(database.get_db)):
    finding = db.query(database.ContrastMammographyLEFinding).filter(
        database.ContrastMammographyLEFinding.id == finding_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    contrast_mammo_id = finding.contrast_mammo_id
    db.delete(finding)
    db.commit()

    renumber_findings(
        db, database.ContrastMammographyLEFinding, "contrast_mammo_id", contrast_mammo_id
    )

    return {"message": "Finding deleted and numbers reordered"}


# ==================== UPDATED CONTRAST MAMMOGRAPHY RC FINDING ENDPOINTS ====================
@app.post("/contrast-mammo-rc-findings/", response_model=schemas.ContrastMammographyRCFinding)
def create_rc_finding(finding: schemas.ContrastMammographyRCFindingCreate, db: Session = Depends(database.get_db)):
    next_number = get_next_finding_number(
        db, database.ContrastMammographyRCFinding, "contrast_mammo_id", finding.contrast_mammo_id
    )

    finding_data = finding.dict()
    finding_data['finding_number'] = next_number

    db_finding = database.ContrastMammographyRCFinding(**finding_data)
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.put("/contrast-mammo-rc-findings/{finding_id}", response_model=schemas.ContrastMammographyRCFinding)
def update_rc_finding(finding_id: int, finding: schemas.ContrastMammographyRCFindingCreate,
                      db: Session = Depends(database.get_db)):
    db_finding = db.query(database.ContrastMammographyRCFinding).filter(
        database.ContrastMammographyRCFinding.id == finding_id
    ).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    old_contrast_mammo_id = db_finding.contrast_mammo_id
    new_contrast_mammo_id = finding.contrast_mammo_id

    for key, value in finding.dict().items():
        setattr(db_finding, key, value)

    if old_contrast_mammo_id != new_contrast_mammo_id:
        next_number = get_next_finding_number(
            db, database.ContrastMammographyRCFinding, "contrast_mammo_id", new_contrast_mammo_id
        )
        db_finding.finding_number = next_number

    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.delete("/contrast-mammo-rc-findings/{finding_id}")
def delete_rc_finding(finding_id: int, db: Session = Depends(database.get_db)):
    finding = db.query(database.ContrastMammographyRCFinding).filter(
        database.ContrastMammographyRCFinding.id == finding_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    contrast_mammo_id = finding.contrast_mammo_id
    db.delete(finding)
    db.commit()

    renumber_findings(
        db, database.ContrastMammographyRCFinding, "contrast_mammo_id", contrast_mammo_id
    )

    return {"message": "Finding deleted and numbers reordered"}


# Добавьте эти эндпоинты в существующий main.py после эндпоинтов контрастной маммографии

# ==================== ULTRASOUND ENDPOINTS (UPDATED) ====================
@app.post("/ultrasounds/", response_model=schemas.Ultrasound)
def create_ultrasound(item: schemas.UltrasoundCreate, db: Session = Depends(database.get_db)):
    db_item = database.Ultrasound(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/ultrasounds/", response_model=List[schemas.Ultrasound])
def get_ultrasounds(patient_id: Optional[str] = None, db: Session = Depends(database.get_db)):
    query = db.query(database.Ultrasound)
    if patient_id:
        query = query.filter(database.Ultrasound.patient_id == patient_id)
    return query.all()


@app.get("/ultrasounds/{item_id}", response_model=schemas.Ultrasound)
def get_ultrasound(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.Ultrasound).filter(database.Ultrasound.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    return item


@app.put("/ultrasounds/{item_id}", response_model=schemas.Ultrasound)
def update_ultrasound(item_id: int, item: schemas.UltrasoundCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(database.Ultrasound).filter(database.Ultrasound.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/ultrasounds/{item_id}")
def delete_ultrasound(item_id: int, db: Session = Depends(database.get_db)):
    item = db.query(database.Ultrasound).filter(database.Ultrasound.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(item)
    db.commit()
    return {"message": "Record deleted"}


# ==================== ULTRASOUND FINDING ENDPOINTS ====================
@app.post("/ultrasound-findings/", response_model=schemas.UltrasoundFinding)
def create_ultrasound_finding(finding: schemas.UltrasoundFindingCreate, db: Session = Depends(database.get_db)):
    next_number = get_next_finding_number(
        db, database.UltrasoundFinding, "ultrasound_id", finding.ultrasound_id
    )

    finding_data = finding.dict()
    finding_data['finding_number'] = next_number

    db_finding = database.UltrasoundFinding(**finding_data)
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.get("/ultrasound-findings/{ultrasound_id}", response_model=List[schemas.UltrasoundFinding])
def get_ultrasound_findings(ultrasound_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.UltrasoundFinding).filter(
        database.UltrasoundFinding.ultrasound_id == ultrasound_id
    ).all()


@app.put("/ultrasound-findings/{finding_id}", response_model=schemas.UltrasoundFinding)
def update_ultrasound_finding(finding_id: int, finding: schemas.UltrasoundFindingCreate,
                              db: Session = Depends(database.get_db)):
    db_finding = db.query(database.UltrasoundFinding).filter(
        database.UltrasoundFinding.id == finding_id
    ).first()
    if not db_finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    old_ultrasound_id = db_finding.ultrasound_id
    new_ultrasound_id = finding.ultrasound_id

    for key, value in finding.dict().items():
        setattr(db_finding, key, value)

    if old_ultrasound_id != new_ultrasound_id:
        next_number = get_next_finding_number(
            db, database.UltrasoundFinding, "ultrasound_id", new_ultrasound_id
        )
        db_finding.finding_number = next_number

    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.delete("/ultrasound-findings/{finding_id}")
def delete_ultrasound_finding(finding_id: int, db: Session = Depends(database.get_db)):
    finding = db.query(database.UltrasoundFinding).filter(
        database.UltrasoundFinding.id == finding_id
    ).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    ultrasound_id = finding.ultrasound_id
    db.delete(finding)
    db.commit()

    renumber_findings(
        db, database.UltrasoundFinding, "ultrasound_id", ultrasound_id
    )

    return {"message": "Finding deleted and numbers reordered"}


# ==================== ULTRASOUND LYMPH NODE ENDPOINTS ====================
@app.post("/ultrasound-lymph-nodes/", response_model=schemas.UltrasoundLymphNode)
def create_ultrasound_lymph_node(lymph_node: schemas.UltrasoundLymphNodeCreate,
                                 db: Session = Depends(database.get_db)):
    next_number = get_next_finding_number(
        db, database.UltrasoundLymphNode, "ultrasound_id", lymph_node.ultrasound_id
    )

    lymph_node_data = lymph_node.dict()
    lymph_node_data['finding_number'] = next_number

    db_lymph_node = database.UltrasoundLymphNode(**lymph_node_data)
    db.add(db_lymph_node)
    db.commit()
    db.refresh(db_lymph_node)
    return db_lymph_node


@app.get("/ultrasound-lymph-nodes/{ultrasound_id}", response_model=List[schemas.UltrasoundLymphNode])
def get_ultrasound_lymph_nodes(ultrasound_id: int, db: Session = Depends(database.get_db)):
    return db.query(database.UltrasoundLymphNode).filter(
        database.UltrasoundLymphNode.ultrasound_id == ultrasound_id
    ).all()


@app.put("/ultrasound-lymph-nodes/{lymph_node_id}", response_model=schemas.UltrasoundLymphNode)
def update_ultrasound_lymph_node(lymph_node_id: int, lymph_node: schemas.UltrasoundLymphNodeCreate,
                                 db: Session = Depends(database.get_db)):
    db_lymph_node = db.query(database.UltrasoundLymphNode).filter(
        database.UltrasoundLymphNode.id == lymph_node_id
    ).first()
    if not db_lymph_node:
        raise HTTPException(status_code=404, detail="Lymph node not found")

    old_ultrasound_id = db_lymph_node.ultrasound_id
    new_ultrasound_id = lymph_node.ultrasound_id

    for key, value in lymph_node.dict().items():
        setattr(db_lymph_node, key, value)

    if old_ultrasound_id != new_ultrasound_id:
        next_number = get_next_finding_number(
            db, database.UltrasoundLymphNode, "ultrasound_id", new_ultrasound_id
        )
        db_lymph_node.finding_number = next_number

    db.commit()
    db.refresh(db_lymph_node)
    return db_lymph_node


@app.delete("/ultrasound-lymph-nodes/{lymph_node_id}")
def delete_ultrasound_lymph_node(lymph_node_id: int, db: Session = Depends(database.get_db)):
    lymph_node = db.query(database.UltrasoundLymphNode).filter(
        database.UltrasoundLymphNode.id == lymph_node_id
    ).first()
    if not lymph_node:
        raise HTTPException(status_code=404, detail="Lymph node not found")

    ultrasound_id = lymph_node.ultrasound_id
    db.delete(lymph_node)
    db.commit()

    renumber_findings(
        db, database.UltrasoundLymphNode, "ultrasound_id", ultrasound_id
    )

    return {"message": "Lymph node deleted and numbers reordered"}