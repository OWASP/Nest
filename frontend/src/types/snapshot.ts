import type { Chapter } from 'types/chapter'
import type { ProjectType } from 'types/project'
import { ReleaseType } from 'types/release'

export type SnapshotDetailsProps = {
  endAt: string
  key: string
  startAt: string
  title: string
  newReleases: ReleaseType[]
  newProjects: ProjectType[]
  newChapters: Chapter[]
}

export type Snapshots = {
  endAt: string
  key: string
  startAt: string
  title: string
}
