import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'
import { ApiError } from '../api/client'
import { getProject, updateProject } from '../api/projects'
import { addMember, listMembers, removeMember } from '../api/memberships'
import { listUsers } from '../api/users'
import { createIssue, deleteIssue, listProjectIssues, updateIssue } from '../api/issues'
import type { Project, ProjectFormValues } from '../types/project'
import type { Membership } from '../types/membership'
import type { User } from '../types/user'
import type { Issue, IssueFormValues } from '../types/issue'
import { LoadingState } from '../components/LoadingState'
import { ErrorMessage } from '../components/ErrorMessage'
import { EmptyState } from '../components/EmptyState'
import { Button } from '../components/Button'
import { Modal } from '../components/Modal'
import { ProjectForm } from '../features/projects/ProjectForm'
import { MemberList } from '../features/members/MemberList'
import { AddMemberForm } from '../features/members/AddMemberForm'
import { IssueRow } from '../features/issues/IssueRow'
import { IssueForm } from '../features/issues/IssueForm'

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [project, setProject] = useState<Project | null>(null)
  const [members, setMembers] = useState<Membership[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [issues, setIssues] = useState<Issue[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [editingProject, setEditingProject] = useState(false)
  const [showAddMember, setShowAddMember] = useState(false)
  const [removingUserId, setRemovingUserId] = useState<string | null>(null)

  const [creatingIssue, setCreatingIssue] = useState(false)
  const [editingIssue, setEditingIssue] = useState<Issue | null>(null)
  const [deletingIssueId, setDeletingIssueId] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!projectId) return
    setLoading(true)
    setError(null)
    try {
      const [projectData, membersData, usersData, issuesData] = await Promise.all([
        getProject(projectId),
        listMembers(projectId),
        listUsers(),
        listProjectIssues(projectId),
      ])
      setProject(projectData)
      setMembers(membersData)
      setUsers(usersData)
      setIssues(issuesData)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load this project.')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => {
    void load()
  }, [load])

  const usersById = useMemo(
    () => new Map(users.map((candidate) => [candidate.id, candidate])),
    [users],
  )
  const memberUserIds = useMemo(() => new Set(members.map((member) => member.user_id)), [members])
  const memberUsers = useMemo(
    () => users.filter((u) => memberUserIds.has(u.id)),
    [users, memberUserIds],
  )
  const nonMemberUsers = useMemo(
    () => users.filter((u) => !memberUserIds.has(u.id)),
    [users, memberUserIds],
  )

  const isOwner = Boolean(project && user && project.owner_id === user.id)

  async function handleUpdateProject(values: ProjectFormValues) {
    if (!projectId) return
    const updated = await updateProject(projectId, values)
    setProject(updated)
    setEditingProject(false)
  }

  async function handleAddMember(userId: string) {
    if (!projectId) return
    const membership = await addMember(projectId, userId)
    setMembers((prev) => [...prev, membership])
  }

  async function handleRemoveMember(userId: string) {
    if (!projectId) return
    setRemovingUserId(userId)
    try {
      await removeMember(projectId, userId)
      setMembers((prev) => prev.filter((member) => member.user_id !== userId))
    } finally {
      setRemovingUserId(null)
    }
  }

  async function handleCreateIssue(values: IssueFormValues) {
    if (!projectId) return
    const issue = await createIssue(projectId, values)
    setIssues((prev) => [...prev, issue])
    setCreatingIssue(false)
  }

  async function handleUpdateIssue(issueId: string, values: IssueFormValues) {
    const updated = await updateIssue(issueId, values)
    setIssues((prev) => prev.map((issue) => (issue.id === issueId ? updated : issue)))
    setEditingIssue(null)
  }

  async function handleDeleteIssue(issueId: string) {
    if (!window.confirm('Delete this issue? This cannot be undone.')) return
    setDeletingIssueId(issueId)
    try {
      await deleteIssue(issueId)
      setIssues((prev) => prev.filter((issue) => issue.id !== issueId))
    } finally {
      setDeletingIssueId(null)
    }
  }

  if (loading) {
    return <LoadingState label="Loading project…" />
  }
  if (error) {
    return <ErrorMessage message={error} />
  }
  if (!project) {
    return null
  }

  return (
    <div className="project-detail">
      <button type="button" className="back-link" onClick={() => navigate('/dashboard')}>
        ← Back to dashboard
      </button>

      <div className="page-header">
        <div>
          <h1>{project.name}</h1>
          <p className="project-detail-description">
            {project.description || 'No description yet.'}
          </p>
        </div>
        {isOwner && (
          <Button type="button" variant="secondary" onClick={() => setEditingProject(true)}>
            Edit project
          </Button>
        )}
      </div>

      <section className="panel">
        <div className="panel-header">
          <h2>Members</h2>
          {isOwner && (
            <Button type="button" onClick={() => setShowAddMember(true)}>
              Add member
            </Button>
          )}
        </div>
        <MemberList
          members={members}
          usersById={usersById}
          currentUserId={user?.id ?? ''}
          canManage={isOwner}
          onRemove={handleRemoveMember}
          removingUserId={removingUserId}
        />
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Issues</h2>
          <Button type="button" onClick={() => setCreatingIssue(true)}>
            New issue
          </Button>
        </div>
        {issues.length === 0 ? (
          <EmptyState
            title="No issues yet"
            description="Create the first issue to start tracking work."
          />
        ) : (
          <ul className="issue-list">
            {issues.map((issue) => (
              <IssueRow
                key={issue.id}
                issue={issue}
                assignee={issue.assignee_id ? (usersById.get(issue.assignee_id) ?? null) : null}
                onEdit={() => setEditingIssue(issue)}
                onDelete={() => handleDeleteIssue(issue.id)}
                deleting={deletingIssueId === issue.id}
              />
            ))}
          </ul>
        )}
      </section>

      {editingProject && (
        <Modal title="Edit project" onClose={() => setEditingProject(false)}>
          <ProjectForm
            initialValues={{ name: project.name, description: project.description }}
            submitLabel="Save changes"
            onSubmit={handleUpdateProject}
            onCancel={() => setEditingProject(false)}
          />
        </Modal>
      )}

      {showAddMember && (
        <Modal title="Add member" onClose={() => setShowAddMember(false)}>
          <AddMemberForm candidates={nonMemberUsers} onAdd={handleAddMember} />
        </Modal>
      )}

      {creatingIssue && (
        <Modal title="New issue" onClose={() => setCreatingIssue(false)}>
          <IssueForm
            members={memberUsers}
            submitLabel="Create issue"
            onSubmit={handleCreateIssue}
            onCancel={() => setCreatingIssue(false)}
          />
        </Modal>
      )}

      {editingIssue && (
        <Modal title="Edit issue" onClose={() => setEditingIssue(null)}>
          <IssueForm
            members={memberUsers}
            initialValues={{
              title: editingIssue.title,
              description: editingIssue.description,
              status: editingIssue.status,
              priority: editingIssue.priority,
              assignee_id: editingIssue.assignee_id,
            }}
            submitLabel="Save changes"
            onSubmit={(values) => handleUpdateIssue(editingIssue.id, values)}
            onCancel={() => setEditingIssue(null)}
          />
        </Modal>
      )}
    </div>
  )
}
