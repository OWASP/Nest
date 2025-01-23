export interface ChapterType {
  created_at: number
  is_active: boolean
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
  _geoloc: { lat: number; lng: number }
}

export interface ChapterDataType {
  active_committees_count: number
  chapters: ChapterType[]
  total_pages: number
}
