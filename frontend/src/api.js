import axios from 'axios'

const API_BASE = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // Patients
  getPatients(params = {}) {
    return api.get('/patients/', { params })
  },
  getPatient(id) {
    return api.get(`/patients/${id}`)
  },
  createPatient(data) {
    return api.post('/patients/', data)
  },
  updatePatient(id, data) {
    return api.put(`/patients/${id}`, data)
  },
  deletePatient(id) {
    return api.delete(`/patients/${id}`)
  },

  // Mammographies
  getMammographies(params = {}) {
    return api.get('/mammographies/', { params })
  },
  getMammography(id) {
    return api.get(`/mammographies/${id}`)
  },
  createMammography(data) {
    return api.post('/mammographies/', data)
  },
  updateMammography(id, data) {
    return api.put(`/mammographies/${id}`, data)
  },
  deleteMammography(id) {
    return api.delete(`/mammographies/${id}`)
  },

  // Mammography Findings
  createMammographyFinding(data) {
    return api.post('/mammography-findings/', data)
  },
  getMammographyFindings(mammoId) {
    return api.get(`/mammography-findings/${mammoId}`)
  },
  deleteMammographyFinding(id) {
    return api.delete(`/mammography-findings/${id}`)
  },

  // Contrast Mammographies
  getContrastMammographies(params = {}) {
    return api.get('/contrast-mammographies/', { params })
  },
  createContrastMammography(data) {
    return api.post('/contrast-mammographies/', data)
  },
  deleteContrastMammography(id) {
    return api.delete(`/contrast-mammographies/${id}`)
  },

  // Ultrasounds
  getUltrasounds(params = {}) {
    return api.get('/ultrasounds/', { params })
  },
  createUltrasound(data) {
    return api.post('/ultrasounds/', data)
  },
  deleteUltrasound(id) {
    return api.delete(`/ultrasounds/${id}`)
  },

  // MRTs
  getMRTs(params = {}) {
    return api.get('/mrts/', { params })
  },
  createMRT(data) {
    return api.post('/mrts/', data)
  },
  deleteMRT(id) {
    return api.delete(`/mrts/${id}`)
  },

  // Histology Biopsies
  getHistologyBiopsies(params = {}) {
    return api.get('/histology-biopsies/', { params })
  },
  createHistologyBiopsy(data) {
    return api.post('/histology-biopsies/', data)
  },
  deleteHistologyBiopsy(id) {
    return api.delete(`/histology-biopsies/${id}`)
  },

  // Cytology Biopsies
  getCytologyBiopsies(params = {}) {
    return api.get('/cytology-biopsies/', { params })
  },
  createCytologyBiopsy(data) {
    return api.post('/cytology-biopsies/', data)
  },
  deleteCytologyBiopsy(id) {
    return api.delete(`/cytology-biopsies/${id}`)
  },

  // Histology Postops
  getHistologyPostops(params = {}) {
    return api.get('/histology-postops/', { params })
  },
  createHistologyPostop(data) {
    return api.post('/histology-postops/', data)
  },
  deleteHistologyPostop(id) {
    return api.delete(`/histology-postops/${id}`)
  }
}