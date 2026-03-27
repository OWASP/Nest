import type { Contributor } from 'types/contributor'

export type Committee = {
  contributorsCount?: number
  createdAt: string
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
  topContributors?: Contributor[]
  updatedAt: string
  url: string
}
