import { TopContributorsTypeGraphql } from './contributor'
import { EventType } from './event'
import { ProjectIssuesType, ProjectReleaseType } from './project'

export type MainPageData = {
  topContributors: TopContributorsTypeGraphql[]
  recentIssues: ProjectIssuesType[]
  recentReleases: ProjectReleaseType[]
  upcomingEvents: EventType[]
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
  sponsors: SponsorType[]
  statsOverview: {
    activeChaptersStats: number
    activeProjectsStats: number
    contributorsStats: number
    countriesStats: number
  }
}

export type SponsorType = {
  imageUrl: string
  name: string
  sponsorType: string
  url: string
}
