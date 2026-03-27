# meddb_cl — Project Context

## Server

- **Host alias**: `meddb` (in `~/.ssh/config`)
- **IP**: `212.193.24.155`
- **User**: `shchegolev`
- **Project path on server**: `/home/shchegolev/meddb_cl/`

## Deployment

- Docker Compose (`docker-compose.yaml`) with 3 services:
  - `postgres` (container: `medical_db`) — PostgreSQL 15, port 5432
  - `backend` (container: `medical_backend`) — FastAPI/Python, port 8000
  - `frontend` (container: `medical_frontend`) — Vue.js, port 3000
- DB credentials: `medical_user` / `medical_pass` / `medical_db`

## Useful Commands

```bash
# Connect to server
ssh meddb

# Run psql on server
ssh meddb 'docker exec medical_db psql -U medical_user -d medical_db -c "..."'

# View backend logs
ssh meddb 'docker logs medical_backend --tail 50'

# Restart services
ssh meddb 'cd /home/shchegolev/meddb_cl && docker-compose restart'
```

## Architecture

- **Backend**: FastAPI (`backend/main.py`), SQLAlchemy models (`backend/database.py`), Pydantic schemas (`backend/schemas.py`)
- **Frontend**: Vue.js SPA (`frontend/src/`), key components in `src/components/`
- **Main report component**: `frontend/src/components/ReportBuilderModal.vue` — Variative Excel report builder

## Database Tables

| Table | Description |
|---|---|
| patients | Patient passport data |
| mammographies / mammography_findings | Mammography studies + findings |
| contrast_mammographies / contrast_mammo_le_findings / contrast_mammo_rc_findings | Contrast mammography LE + RC |
| ultrasounds / ultrasound_findings / ultrasound_lymph_nodes | Ultrasound MZH + LU |
| mrts / mrt_findings / mrt_lymph_nodes | MRI MZH + LU |
| histology_biopsies / histology_biopsy_findings | Histology (biopsy) |
| histology_postops / histology_postop_findings | Histology (post-op) |
| cytology_biopsies / cytology_biopsy_findings | Cytology (biopsy) |
