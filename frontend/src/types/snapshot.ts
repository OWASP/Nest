import type { Chapter } from 'types/chapter'
import type { Project } from 'types/project'
import type { Release } from 'types/release'

export type SnapshotDetails = {
  endAt: number
  key: string
  startAt: number
  title: string
  newReleases: Release[]
  newProjects: Project[]
  newChapters: Chapter[]
}

export type Snapshot = {
  endAt: number
  key: string
  startAt: number
  title: string
}
