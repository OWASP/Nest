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
export interface Program {
  id: string
  name: string
  description: string
  status: ProgramStatusEnum
  experienceLevels: ExperienceLevelEnum[]
  menteesLimit: number
  startedAt: string
  endedAt: string
  domains: string[]
  tags: string[]
  admins: Contributor[]
}
