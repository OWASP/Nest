import { ChapterTypeGraphQL } from 'types/chapter'
import { ProjectTypeGraphql } from 'types/project'

export interface TopContributorTypeGraphql {
  avatarUrl: string
  contributionsCount: number
  login: string
  name: string
}

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
  newProjects: ProjectTypeGraphql[]
  newChapters: ChapterTypeGraphQL[]
  topContributors: TopContributorTypeGraphql[]
}

export interface Snapshots {
  endAt: string
  key: string
  startAt: string
  title: string
}
