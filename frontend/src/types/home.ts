import { TopContributorsTypeGraphql } from './contributor'
import { ProjectIssuesType, ProjectReleaseType } from './project'

export type MainPageData = {
  topContributors: TopContributorsTypeGraphql[]
  recentIssues: ProjectIssuesType[]
  recentReleases: ProjectReleaseType[]
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
  statsOverview: {
    activeChaptersStats: number
    activeProjectsStats: number
    contributorsStats: number
    countriesStats: number
  }
}
