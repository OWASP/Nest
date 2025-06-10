import { TopContributorsType } from 'types/contributor'

export interface CommitteeType {
  createdAt: number
  key: string
  leaders: string[]
  name: string
  objectID?: string
  relatedUrls: string[]
  topContributors: TopContributorsType[]
  summary: string
  updatedAt: number
  url: string
  contributorsCount?: number
  forksCount?: number
  issuesCount?: number
  starsCount?: number
  repositoriesCount?: number
}
