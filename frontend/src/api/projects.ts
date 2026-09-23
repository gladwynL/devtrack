import { apiRequest } from './client'
import type { Project, ProjectFormValues } from '../types/project'

export function listProjects(): Promise<Project[]> {
  return apiRequest<Project[]>('/api/projects')
}

export function getProject(projectId: string): Promise<Project> {
  return apiRequest<Project>(`/api/projects/${projectId}`)
}

export function createProject(input: ProjectFormValues): Promise<Project> {
  return apiRequest<Project>('/api/projects', { method: 'POST', body: input })
}

export function updateProject(
  projectId: string,
  input: Partial<ProjectFormValues>,
): Promise<Project> {
  return apiRequest<Project>(`/api/projects/${projectId}`, { method: 'PATCH', body: input })
}
