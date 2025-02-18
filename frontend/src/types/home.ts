import { TopContributorsTypeGraphql } from './contributor'
import { ProjectIssuesType, ProjectReleaseType } from './project'

export type MainPageData = {
  topContributors: TopContributorsTypeGraphql[]
  recentIssue: ProjectIssuesType[]
  recentRelease: ProjectReleaseType[]
  countsOverview: {
    chaptersCount: number
    countriesCount: number
    activeProjectsCount: number
    contributorsCount: number
  }
  recentChapters: {
    name: string
    suggestedLocation: string
    region: string
    key: string
    topContributors: {
      name: string
    }[]
  }[]
  recentProjects: {
    name: string
    type: string
    createdAt: string
    key: string
    openIssuesCount: number
    repositoriesCount: number
  }[]
}
