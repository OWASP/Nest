import { TopContributorsTypeGraphql } from './contributor'

export interface CommitteeTypeAlgolia {
  created_at: number
  key: string
  leaders: string[]
  name: string
  related_urls: string[]
  top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  summary: string
  updated_at: number
  url: string
  objectID: string
}

export interface CommitteeDetailsTypeGraphQL {
  contributorsCount: number
  createdAt: number
  forksCount: number
  issuesCount: number
  leaders: string[]
  name: string
  relatedUrls: string[]
  starsCount: number
  topContributors: TopContributorsTypeGraphql[]
  repositoriesCount: number
  summary: string
  updatedAt: number
  url: string
}

export interface CommitteeDataType {
  active_committees_count: number
  committees: CommitteeTypeAlgolia[]
  total_pages: number
}
