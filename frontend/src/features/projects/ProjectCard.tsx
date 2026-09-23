import { Link } from 'react-router-dom'
import type { Project } from '../../types/project'

interface ProjectCardProps {
  project: Project
  isOwner: boolean
}

export function ProjectCard({ project, isOwner }: ProjectCardProps) {
  return (
    <Link to={`/projects/${project.id}`} className="project-card">
      <div className="project-card-header">
        <h3>{project.name}</h3>
        <span className={`role-badge ${isOwner ? 'role-owner' : 'role-member'}`}>
          {isOwner ? 'Owner' : 'Member'}
        </span>
      </div>
      <p className="project-card-description">{project.description || 'No description yet.'}</p>
    </Link>
  )
}
