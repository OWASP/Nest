import { TopContributors } from 'types/contributor'

export interface Committee {
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
