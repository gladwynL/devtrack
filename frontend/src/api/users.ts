import { apiRequest } from './client'
import type { User } from '../types/user'

export function listUsers(): Promise<User[]> {
  return apiRequest<User[]>('/api/users')
}
