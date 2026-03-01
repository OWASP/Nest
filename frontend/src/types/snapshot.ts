import type { Chapter } from 'types/chapter'
import type { Project } from 'types/project'
import type { Release } from 'types/release'

export type SnapshotDetails = {
  endAt: string
  key: string
  startAt: string
  title: string
  newReleases: Release[]
  newProjects: Project[]
  newChapters: Chapter[]
}

export type Snapshot = {
  endAt: string
  key: string
  startAt: string
  title: string
}
