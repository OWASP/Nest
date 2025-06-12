import type { Chapter } from 'types/chapter'
import type { Project } from 'types/project'
import type { Release } from 'types/release'

export type SnapshotDetailsProps = {
  endAt: string
  key: string
  startAt: string
  title: string
  newReleases: Release[]
  newProjects: Project[]
  newChapters: Chapter[]
}

export type Snapshots = {
  endAt: string
  key: string
  startAt: string
  title: string
}
