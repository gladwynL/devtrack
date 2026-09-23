import { apiRequest } from './client'
import type { LoginInput, RegisterInput, TokenResponse } from '../types/auth'
import type { User } from '../types/user'

export function register(input: RegisterInput): Promise<User> {
  return apiRequest<User>('/api/auth/register', { method: 'POST', body: input, auth: false })
}

export function login(input: LoginInput): Promise<TokenResponse> {
  return apiRequest<TokenResponse>('/api/auth/login', { method: 'POST', body: input, auth: false })
}

export function fetchCurrentUser(): Promise<User> {
  return apiRequest<User>('/api/auth/me')
}
