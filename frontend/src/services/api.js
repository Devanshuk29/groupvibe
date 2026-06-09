import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const createSession = (data) => api.post('/api/sessions/create', data)
export const getSession = (sessionId) => api.get(`/api/sessions/${sessionId}`)
export const submitPreferences = (sessionId, data) => api.post(`/api/sessions/${sessionId}/submit-preferences`, data)
export const generateRecommendations = (sessionId) => api.post(`/api/sessions/${sessionId}/generate-recommendations`, {})

export const getPlaces = () => api.get('/api/places')
export const voteForPlace = (sessionId, data) => api.post(`/api/sessions/${sessionId}/vote`, data)
export const getVotes = (sessionId) => api.get(`/api/sessions/${sessionId}/votes`)

export default api