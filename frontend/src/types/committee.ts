import { TopContributorsType } from 'types/contributor'

export interface CommitteeBase {
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
}

export interface CommitteeDetailsType extends CommitteeBase {
  contributorsCount: number
  forksCount: number
  issuesCount: number
  starsCount: number
  repositoriesCount: number
}
