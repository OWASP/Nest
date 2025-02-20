import { TopContributorsTypeGraphql } from './contributor'
import { ProjectIssuesType, ProjectReleaseType } from './project'

export type MainPageData = {
  topContributors: TopContributorsTypeGraphql[]
  recentIssue: ProjectIssuesType[]
  recentRelease: ProjectReleaseType[]
  countsOverview: {
    activeProjectsCount: number
    chaptersCount: number
    contributorsCount: number
    countriesCount: number
  }
  recentChapters: {
    name: string
    createdAt: string
    key: string
    region: string
    suggestedLocation: string
    topContributors: {
      name: string
    }[]
  }[]
  recentProjects: {
    createdAt: string
    key: string
    name: string
    openIssuesCount: number
    repositoriesCount: number
    type: string
  }[]
}
