import type { TopContributors } from 'types/contributor'

export type Committee = {
  contributorsCount?: number
  createdAt: number
  forksCount?: number
  issuesCount?: number
  key: string
  leaders: string[]
  name: string
  objectID?: string
  relatedUrls: string[]
  repositoriesCount?: number
  starsCount?: number
  summary: string
  topContributors: TopContributors[]
  updatedAt: number
  url: string
}
