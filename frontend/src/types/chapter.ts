import { topContributorsType } from './contributor'

export interface ChapterType {
  created_at: number
  is_active: boolean
  key: string
  leaders: string[]
  name: string
  related_urls: string[]
  top_contributors: topContributorsType[]
  region: string
  summary: string
  suggested_location: string
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
