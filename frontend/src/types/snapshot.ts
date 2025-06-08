import { ChapterType } from 'types/chapter'
import { ProjectType } from 'types/project'

export interface ReleaseType {
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
  newChapters: ChapterType[]
}

export interface Snapshots {
  endAt: string
  key: string
  startAt: string
  title: string
}
