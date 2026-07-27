import apiClient from './client.js'

export function askAssistant(question) {
  return apiClient.post('/assistant/queries/ask/', { question })
}
export function getMyQueries() {
  return apiClient.get('/assistant/queries/')
}