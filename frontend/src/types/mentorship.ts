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

export const EXPERIENCE_LEVELS = {
  BEGINNER: 'BEGINNER',
  INTERMEDIATE: 'INTERMEDIATE',
  ADVANCED: 'ADVANCED',
}

// Main Program type
export type Program = {
  id: string
  key: string
  name: string
  description: string
  status: ProgramStatusEnum
  experienceLevels?: ExperienceLevelEnum[]
  menteesLimit?: number
  startedAt: string
  endedAt: string
  domains?: string[]
  tags?: string[]
  userRole?: string
  admins?: Contributor[]
  modules?: Module[]
}

export type ProgramList = {
  objectId: string
  name: string
  description: string
  experienceLevels: string[]
  status: string
  key: string
  admins: { name: string; login: string }[]
  startedAt: string
  endedAt: string
  modules: string[]
}

export type Module = {
  id: string
  key: string
  name: string
  description: string
  status: ProgramStatusEnum
  experienceLevel: ExperienceLevelEnum
  mentors: Contributor[]
  mentees?: Contributor[]
  startedAt: string
  endedAt: string
  domains: string[]
  tags: string[]
  labels: string[]
}

export type ModuleFormData = {
  name: string
  description: string
  experienceLevel: string
  startedAt: string
  endedAt: string
  domains: string
  tags: string
  labels: string
  projectName: string
  projectId: string
  mentorLogins: string
}

import type { Issue } from 'types/issue'

export type CompletedLevel = {
  id: string
  name: string
  level: number
  completedAt: string
  stack: string
  description: string
}

export type Achievement = {
  id: string
  name: string
  description: string
  earnedAt: string
  type: string
  points: number
}

export type Penalty = {
  id: string
  reason: string
  points: number
  createdAt: string
  status: string
  description: string
}

export type MenteeDetails = {
  id: string
  login: string
  name: string
  avatarUrl: string
  email?: string
  bio?: string
  completedLevels: CompletedLevel[]
  achievements: Achievement[]
  penalties: Penalty[]
  openIssues: Issue[]
  closedIssues: Issue[]
}
