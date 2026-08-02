import apiClient from './client.js'

export function login(phone, password) {
  return apiClient.post('/accounts/tokenobtainpair/', { phone, password })
}

export function refreshToken() {
  return apiClient.post('/accounts/tokenrefresh/')
}

export function logout() { 
  return apiClient.post('/accounts/logout/')
}

export function register(payload) {
  return apiClient.post('/accounts/users/', payload)
}

export function fetchProfile() {
  return apiClient.get('/accounts/users/profile/')
}

export function updateProfile(payload) {
  return apiClient.patch('/accounts/users/profile/', payload)
}

export function uploadVerificationDocument(documentType, file) {
  const formData = new FormData()
  formData.append('document_type', documentType)
  formData.append('file', file)
  return apiClient.post('/accounts/users/upload_verification_document/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function requestPasswordReset(phone) {
  return apiClient.post('/accounts/password-reset/request/', { phone })
}

export function verifyPasswordResetOTP(resetReference, otpCode) {
  return apiClient.post('/accounts/password-reset/verify/', { reset_reference: resetReference, otp_code: otpCode })
}

export function completePasswordReset(resetReference, newPassword) {
  return apiClient.post('/accounts/password-reset/complete/', { reset_reference: resetReference, new_password: newPassword })
}