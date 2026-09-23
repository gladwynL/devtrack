import { apiRequest } from './client'
import type { Membership, MembershipRole } from '../types/membership'

export function listMembers(projectId: string): Promise<Membership[]> {
  return apiRequest<Membership[]>(`/api/projects/${projectId}/members`)
}

export function addMember(
  projectId: string,
  userId: string,
  role: MembershipRole = 'member',
): Promise<Membership> {
  return apiRequest<Membership>(`/api/projects/${projectId}/members`, {
    method: 'POST',
    body: { user_id: userId, role },
  })
}

export function removeMember(projectId: string, userId: string): Promise<void> {
  return apiRequest<void>(`/api/projects/${projectId}/members/${userId}`, { method: 'DELETE' })
}
