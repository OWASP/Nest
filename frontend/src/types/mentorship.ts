import type { Contributor } from 'types/contributor'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { PullRequest } from 'types/pullRequest'
// eslint-disable-next-line no-restricted-imports
import { ExperienceLevelEnum, ProgramStatusEnum } from './__generated__/graphql'

// Main Program type
export type Program = {
  id: string
  key: string
  name: string
  description: string
  status?: ProgramStatusEnum
  experienceLevels?: ExperienceLevelEnum[]
  menteesLimit?: number
  startedAt: string
  endedAt: string
  domains?: string[]
  tags?: string[]
  userRole?: string | null
  admins?: Contributor[]
  modules?: Module[]
  recentMilestones?: Milestone[]
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
  description: string
  domains?: string[] | null
  endedAt: string | number
  experienceLevel: ExperienceLevelEnum
  id: string
  key: string
  labels?: string[] | null
  mentees?: Contributor[]
  mentors: Contributor[]
  name: string
  startedAt: string | number
  status?: ProgramStatusEnum
  tags?: string[] | null
  recentPullRequests?: PullRequest[]
  projectId?: string | null
  projectName?: string | null
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
  bio?: string | null
  domains?: string[] | null
  tags?: string[] | null
  experienceLevel?: string
  completedLevels?: CompletedLevel[]
  achievements?: Achievement[]
  penalties?: Penalty[]
  openIssues?: Issue[]
  closedIssues?: Issue[]
}
