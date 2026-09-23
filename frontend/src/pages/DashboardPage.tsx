import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'
import { useAsync } from '../hooks/useAsync'
import { listProjects, createProject } from '../api/projects'
import type { ProjectFormValues } from '../types/project'
import { LoadingState } from '../components/LoadingState'
import { ErrorMessage } from '../components/ErrorMessage'
import { EmptyState } from '../components/EmptyState'
import { Button } from '../components/Button'
import { Modal } from '../components/Modal'
import { ProjectCard } from '../features/projects/ProjectCard'
import { ProjectForm } from '../features/projects/ProjectForm'

export function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const fetchProjects = useCallback(() => listProjects(), [])
  const { data: projects, loading, error } = useAsync(fetchProjects)
  const [showCreate, setShowCreate] = useState(false)

  async function handleCreate(values: ProjectFormValues) {
    const project = await createProject(values)
    setShowCreate(false)
    navigate(`/projects/${project.id}`)
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <div>
          <h1>Your projects</h1>
          <p className="muted">Signed in as {user?.display_name}</p>
        </div>
        <Button type="button" onClick={() => setShowCreate(true)}>
          New project
        </Button>
      </div>

      {loading && <LoadingState label="Loading projects…" />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && projects && projects.length === 0 && (
        <EmptyState
          title="No projects yet"
          description="Create your first project to start tracking issues."
          action={
            <Button type="button" onClick={() => setShowCreate(true)}>
              Create a project
            </Button>
          }
        />
      )}

      {!loading && !error && projects && projects.length > 0 && (
        <div className="project-grid">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              isOwner={project.owner_id === user?.id}
            />
          ))}
        </div>
      )}

      {showCreate && (
        <Modal title="Create project" onClose={() => setShowCreate(false)}>
          <ProjectForm
            submitLabel="Create project"
            onSubmit={handleCreate}
            onCancel={() => setShowCreate(false)}
          />
        </Modal>
      )}
    </div>
  )
}
