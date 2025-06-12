import type { Chapter } from 'types/chapter'
import type { TopContributors } from 'types/contributor'
import type { EventType } from 'types/event'
import type { IssueType } from 'types/issue'
import type { MilestonesType } from 'types/milestone'
import { ProjectType } from 'types/project'
import type { PullRequestType } from 'types/pullRequest'
import type { ReleaseType } from 'types/release'

export type MainPageData = {
  topContributors: TopContributors[]
  recentIssues: IssueType[]
  recentReleases: ReleaseType[]
  upcomingEvents: EventType[]
  recentPullRequests: PullRequestType[]
  recentMilestones: MilestonesType[]
  recentChapters: Chapter[]
  recentPosts: {
    authorName: string
    authorImageUrl: string
    publishedAt: string
    title: string
    url: string
  }[]
  recentProjects: ProjectType[]
  sponsors: SponsorType[]
  statsOverview: {
    activeChaptersStats: number
    activeProjectsStats: number
    contributorsStats: number
    countriesStats: number
    slackWorkspaceStats: number
  }
}

export type SponsorType = {
  imageUrl: string
  name: string
  sponsorType: string
  url: string
}
