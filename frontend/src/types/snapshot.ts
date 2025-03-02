import { ChapterTypeGraphQL } from 'types/chapter'
import { ProjectTypeGraphql } from 'types/project'

export interface ReleaseType {
  name: string
  publishedAt: string
  tagName: string
  projectName: string
}

export interface SnapshotDetailsProps {
  title: string
  key: string
  updatedAt: string
  createdAt: string
  startAt: string
  endAt: string
  status: string
  errorMessage: string
  newReleases: ReleaseType[]
  newProjects: ProjectTypeGraphql[]
  newChapters: ChapterTypeGraphQL[]
}
