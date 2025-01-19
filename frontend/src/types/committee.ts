export interface CommitteeType {
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

export interface CommitteeDataType {
  active_committees_count: number
  committees: CommitteeType[]
  total_pages: number
}
