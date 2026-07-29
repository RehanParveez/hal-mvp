import apiClient from './client.js'

export function askAssistant(question, extraParams = {}) {
  return apiClient.post('/assistant/queries/ask/', { question, extraParams})
}
export function getMyQueries() {
  return apiClient.get('/assistant/queries/')
}

export function getSeasonSummary(invoiceId) {
  return apiClient.get(`/assistant/season-summary/${invoiceId}/`)
}