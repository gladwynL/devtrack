export interface Project {
  id: string
  name: string
  description: string | null
  owner_id: string
  created_at: string
  updated_at: string
}

/** Shape produced by the create/edit project form; the API layer narrows
 * this to Partial<ProjectFormValues> for updates. */
export interface ProjectFormValues {
  name: string
  description: string | null
}
