export interface CommitteeType {
  idx_created_at: number
  idx_key: string
  idx_leaders: string[]
  idx_name: string
  idx_related_urls: string[]
  idx_top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  idx_summary: string
  idx_updated_at: number
  idx_url: string
  objectID: string
}

export interface CommitteeDataType {
  active_committees_count: number
  committees: CommitteeType[]
  total_pages: number
}
