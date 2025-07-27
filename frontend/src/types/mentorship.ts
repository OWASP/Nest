import type { Contributor } from 'types/contributor'
export enum ExperienceLevelEnum {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export enum ProgramStatusEnum {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  COMPLETED = 'completed',
}

// Main Program type
export type Program = {
  id: string
  key: string
  name: string
  description: string
  status: ProgramStatusEnum
  experienceLevels: ExperienceLevelEnum[]
  menteesLimit: number
  startedAt: string
  endedAt: string
  domains: string[]
  tags: string[]
  userRole?: string
  admins: Contributor[]
  modules: Module[]
}

export type Module = {
  id: string
  key: string
  name: string
  description: string
  status: ProgramStatusEnum
  experienceLevel: ExperienceLevelEnum
  mentors: Contributor[]
  startedAt: string
  endedAt: string
  domains: string[]
  tags: string[]
}

export type ModuleFormData = {
  name: string
  description: string
  experienceLevel: string
  startedAt: string
  endedAt: string
  domains: string
  tags: string
  projectName: string
  projectId: string
  mentorLogins: string
}
