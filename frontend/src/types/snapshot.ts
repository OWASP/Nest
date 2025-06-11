import { Chapter } from 'types/chapter'
import { ProjectType } from 'types/project'

export type ReleaseType = {
  name: string
  publishedAt: string
  tagName: string
  projectName: string
}

export interface SnapshotDetailsProps {
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
