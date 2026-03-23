import axios from 'axios'

// Определяем базовый URL в зависимости от окружения
const getApiBaseUrl = () => {
  // Если есть переменная окружения, используем её
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // Автоматическое определение
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000'
  }
  
  // Для удаленного сервера используем текущий хост с портом 8000
  return `http://${window.location.hostname}:8000`
}

const API_BASE = getApiBaseUrl()

console.log('API Base URL:', API_BASE) // Для отладки

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
  updateMammographyFinding(id, data) {
    return api.put(`/mammography-findings/${id}`, data)
  },
  deleteMammographyFinding(id) {
    return api.delete(`/mammography-findings/${id}`)
  },

  // Contrast Mammographies
  getContrastMammographies(params = {}) {
    return api.get('/contrast-mammographies/', { params })
  },
  getContrastMammography(id) {
    return api.get(`/contrast-mammographies/${id}`)
  },
  createContrastMammography(data) {
    return api.post('/contrast-mammographies/', data)
  },
  updateContrastMammography(id, data) {
    return api.put(`/contrast-mammographies/${id}`, data)
  },
  deleteContrastMammography(id) {
    return api.delete(`/contrast-mammographies/${id}`)
  },

  // Contrast Mammography LE Findings
  createContrastMammoLEFinding(data) {
    return api.post('/contrast-mammo-le-findings/', data)
  },
  getContrastMammoLEFindings(mammoId) {
    return api.get(`/contrast-mammo-le-findings/${mammoId}`)
  },
  updateContrastMammoLEFinding(id, data) {
    return api.put(`/contrast-mammo-le-findings/${id}`, data)
  },
  deleteContrastMammoLEFinding(id) {
    return api.delete(`/contrast-mammo-le-findings/${id}`)
  },

  // Contrast Mammography RC Findings
  createContrastMammoRCFinding(data) {
    return api.post('/contrast-mammo-rc-findings/', data)
  },
  getContrastMammoRCFindings(mammoId) {
    return api.get(`/contrast-mammo-rc-findings/${mammoId}`)
  },
  updateContrastMammoRCFinding(id, data) {
    return api.put(`/contrast-mammo-rc-findings/${id}`, data)
  },
  deleteContrastMammoRCFinding(id) {
    return api.delete(`/contrast-mammo-rc-findings/${id}`)
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

  // MRT Findings
  getMRTFindings(mrtId) {
    return api.get(`/mrt-findings/${mrtId}`)
  },
  createMRTFinding(data) {
    return api.post('/mrt-findings/', data)
  },
  updateMRTFinding(id, data) {
    return api.put(`/mrt-findings/${id}`, data)
  },
  deleteMRTFinding(id) {
    return api.delete(`/mrt-findings/${id}`)
  },

  // MRT Lymph Nodes
  getMRTLymphNodes(mrtId) {
    return api.get(`/mrt-lymph-nodes/${mrtId}`)
  },
  createMRTLymphNode(data) {
    return api.post('/mrt-lymph-nodes/', data)
  },
  updateMRTLymphNode(id, data) {
    return api.put(`/mrt-lymph-nodes/${id}`, data)
  },
  deleteMRTLymphNode(id) {
    return api.delete(`/mrt-lymph-nodes/${id}`)
  },

  // Histology Biopsies
  getHistologyBiopsies(params = {}) {
    return api.get('/histology-biopsies/', { params })
  },
  getHistologyBiopsy(id) {
    return api.get(`/histology-biopsies/${id}`)
  },
  createHistologyBiopsy(data) {
    return api.post('/histology-biopsies/', data)
  },
  updateHistologyBiopsy(id, data) {
    return api.put(`/histology-biopsies/${id}`, data)
  },
  deleteHistologyBiopsy(id) {
    return api.delete(`/histology-biopsies/${id}`)
  },

  // Histology Biopsy Findings
  createHistologyBiopsyFinding(data) {
    return api.post('/histology-biopsy-findings/', data)
  },
  getHistologyBiopsyFindings(hbId) {
    return api.get(`/histology-biopsy-findings/${hbId}`)
  },
  updateHistologyBiopsyFinding(id, data) {
    return api.put(`/histology-biopsy-findings/${id}`, data)
  },
  deleteHistologyBiopsyFinding(id) {
    return api.delete(`/histology-biopsy-findings/${id}`)
  },


  // Cytology Biopsies
  getCytologyBiopsies(params = {}) {
    return api.get('/cytology-biopsies/', { params })
  },
  createCytologyBiopsy(data) {
    return api.post('/cytology-biopsies/', data)
  },
  updateCytologyBiopsy(id, data) {
    return api.put(`/cytology-biopsies/${id}`, data)
  },
  deleteCytologyBiopsy(id) {
    return api.delete(`/cytology-biopsies/${id}`)
  },

    // Histology Biopsy Findings
  createCytologyBiopsyFinding(data) {
    return api.post('/cytology-biopsy-findings/', data)
  },
  getCytologyBiopsyFindings(hbId) {
    return api.get(`/cytology-biopsy-findings/${hbId}`)
  },
  updateCytologyBiopsyFinding(id, data) {
    return api.put(`/cytology-biopsy-findings/${id}`, data)
  },
  deleteCytologyBiopsyFinding(id) {
    return api.delete(`/cytology-biopsy-findings/${id}`)
  },

  // Histology Postops
  getHistologyPostops(params = {}) {
    return api.get('/histology-postops/', { params })
  },
  createHistologyPostop(data) {
    return api.post('/histology-postops/', data)
  },
  updateHistologyPostop(id, data) {
    return api.put(`/histology-postops/${id}`, data)
  },
  deleteHistologyPostop(id) {
    return api.delete(`/histology-postops/${id}`)
  },

  // ==================== ULTRASOUND API METHODS ====================

  getUltrasounds(patientId) {
    return api.get('/ultrasounds/', {
      params: { patient_id: patientId }
    })
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

  // Ultrasound Findings
  getUltrasoundFindings(ultrasoundId) {
    return api.get(`/ultrasound-findings/${ultrasoundId}`)
  },

  createUltrasoundFinding(data) {
    return api.post('/ultrasound-findings/', data)
  },

  updateUltrasoundFinding(id, data) {
    return api.put(`/ultrasound-findings/${id}`, data)
  },

  deleteUltrasoundFinding(id) {
    return api.delete(`/ultrasound-findings/${id}`)
  },

  // Ultrasound Lymph Nodes
  getUltrasoundLymphNodes(ultrasoundId) {
    return api.get(`/ultrasound-lymph-nodes/${ultrasoundId}`)
  },

  createUltrasoundLymphNode(data) {
    return api.post('/ultrasound-lymph-nodes/', data)
  },

  updateUltrasoundLymphNode(id, data) {
    return api.put(`/ultrasound-lymph-nodes/${id}`, data)
  },

  deleteUltrasoundLymphNode(id) {
    return api.delete(`/ultrasound-lymph-nodes/${id}`)
  },

  // Histology Postop Findings
  getHistologyPostopFindings(histologyPostopId) {
    return api.get(`/histology-postop-findings/${histologyPostopId}`)
  },

  createHistologyPostopFinding(data) {
    return api.post('/histology-postop-findings/', data)
  },

  updateHistologyPostopFinding(id, data) {
    return api.put(`/histology-postop-findings/${id}`, data)
  },

  deleteHistologyPostopFinding(id) {
    return api.delete(`/histology-postop-findings/${id}`)
  }
}