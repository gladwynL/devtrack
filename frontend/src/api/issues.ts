import { apiRequest } from './client'
import type { Issue, IssueFormValues } from '../types/issue'
import type { IssueActivity } from '../types/activity'

export function listProjectIssues(projectId: string): Promise<Issue[]> {
  return apiRequest<Issue[]>(`/api/projects/${projectId}/issues`)
}

export function createIssue(projectId: string, input: IssueFormValues): Promise<Issue> {
  return apiRequest<Issue>(`/api/projects/${projectId}/issues`, { method: 'POST', body: input })
}

export function updateIssue(issueId: string, input: Partial<IssueFormValues>): Promise<Issue> {
  return apiRequest<Issue>(`/api/issues/${issueId}`, { method: 'PATCH', body: input })
}

export function deleteIssue(issueId: string): Promise<void> {
  return apiRequest<void>(`/api/issues/${issueId}`, { method: 'DELETE' })
}

export function listIssueActivity(issueId: string): Promise<IssueActivity[]> {
  return apiRequest<IssueActivity[]>(`/api/issues/${issueId}/activity`)
}
