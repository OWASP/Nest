import { TopContributorsType } from './contributor'

export interface ChapterType {
  createdAt: number
  isActive: boolean
  key: string
  leaders: string[]
  name: string
  relatedUrls: string[]
  topContributors: TopContributorsType[]
  region: string
  summary: string
  suggestedLocation: string
  updatedAt: number
  url: string
  geoLocation: GeoLocation
}

export interface GeoLocation{
  lat: number
  lng: number
}


export interface GeoLocData {
  geoLocation: GeoLocation
  name: string
  key: string
}

export interface ChapterDataType {
  active_committees_count: number
  chapters: ChapterType[]
  total_pages: number
}
