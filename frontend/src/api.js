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

  // Ultrasounds
  getUltrasounds(params = {}) {
    return api.get('/ultrasounds/', { params })
  },
  getUltrasound(id) {
    return api.get(`/ultrasounds/${id}`)
  },
  createUltrasound(data) {
    return api.post('/ultrasounds/', data)
  },
  updateUltrasound(id, data) {
    return api.put(`/ultrasounds/${id}`, data)
  },
  deleteUltrasound(id) {
    return api.delete(`/ultrasounds/${id}`)
  },

  // MRTs
  getMRTs(params = {}) {
    return api.get('/mrts/', { params })
  },
  getMRT(id) {
    return api.get(`/mrts/${id}`)
  },
  createMRT(data) {
    return api.post('/mrts/', data)
  },
  updateMRT(id, data) {
    return api.put(`/mrts/${id}`, data)
  },
  deleteMRT(id) {
    return api.delete(`/mrts/${id}`)
  },

  // Export
  exportData(tableName, params = {}) {
    return api.get(`/export/${tableName}`, {
      params,
      responseType: 'blob'
    })
  }
}