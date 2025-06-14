import type { Chapter } from 'types/chapter'
import type { Contributor } from 'types/contributor'
import type { Event } from 'types/event'
import type { Issue } from 'types/issue'
import type { Milestone } from 'types/milestone'
import type { Project } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'

export type MainPageData = {
  topContributors: Contributor[]
  recentIssues: Issue[]
  recentReleases: Release[]
  upcomingEvents: Event[]
  recentPullRequests: PullRequest[]
  recentMilestones: Milestone[]
  recentChapters: Chapter[]
  recentPosts: {
    authorName: string
    authorImageUrl: string
    publishedAt: string
    title: string
    url: string
  }[]
  recentProjects: Project[]
  sponsors: Sponsor[]
  statsOverview: {
    activeChaptersStats: number
    activeProjectsStats: number
    contributorsStats: number
    countriesStats: number
    slackWorkspaceStats: number
  }
}

export type Sponsor = {
  imageUrl: string
  name: string
  sponsorType: string
  url: string
}
