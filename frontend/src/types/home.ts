import { TopContributorsTypeGraphql } from './contributor'
import { EventType } from './event'
import { ProjectIssuesType, ProjectReleaseType } from './project'

export type MainPageData = {
  topContributors: TopContributorsTypeGraphql[]
  recentIssues: ProjectIssuesType[]
  recentReleases: ProjectReleaseType[]
  upcomingEvents: EventType[]
  recentPullRequests: PullRequestsType[]
  recentChapters: {
    createdAt: string
    key: string
    leaders: string[]
    name: string
    suggestedLocation: string
  }[]
  recentPosts: {
    authorName: string
    authorImageUrl: string
    publishedAt: string
    title: string
    url: string
  }[]
  recentProjects: {
    createdAt: string
    key: string
    leaders: string[]
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

export type PullRequestsType = {
  createdAt: string
  title: string
  url: string
  author: {
    login: string
    avatarUrl: string
    name: string
  }
}
