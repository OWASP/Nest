import type { Chapter } from 'types/chapter'
import type { Event } from 'types/event'
import type { Project } from 'types/project'
import type { Release } from 'types/release'

export type SnapshotPullRequest = {
  id: string
  author?: {
    avatarUrl: string
    id: string
    login: string
    name: string
  } | null
  createdAt: string
  organizationName?: string | null
  repositoryName?: string | null
  state: string
  title: string
  url: string
}

export type SnapshotPost = {
  id: string
  authorImageUrl: string
  authorName: string
  publishedAt: string
  title: string
  url: string
}

export type SnapshotIssue = {
  id: string
  author?: {
    avatarUrl: string
    id: string
    login: string
    name: string
  } | null
  createdAt: string
  organizationName?: string | null
  repositoryName?: string | null
  state: string
  title: string
  url: string
}

export type SnapshotUser = {
  id: string
  avatarUrl: string
  login: string
  name: string
  createdAt: string
}

export type SnapshotDetails = {
  endAt: string
  key: string
  startAt: string
  title: string
  chapters: Chapter[]
  events: Event[]
  issues: SnapshotIssue[]
  posts: SnapshotPost[]
  projects: Project[]
  pullRequests: SnapshotPullRequest[]
  releases: Release[]
  users: SnapshotUser[]
}

export type Snapshot = {
  endAt: string
  key: string
  startAt: string
  title: string
}
