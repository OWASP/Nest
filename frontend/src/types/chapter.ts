import { TopContributorsTypeAlgolia } from './contributor'

export interface ChapterDataType {
  active_committees_count: number
  chapters: ChapterTypeAlgolia[]
  total_pages: number
}

export interface ChapterTypeAlgolia {
  _geoloc: { lat: number; lng: number }
  created_at: number
  is_active: boolean
  key: string
  leaders: string[]
  name: string
  objectID: string
  region: string
  related_urls: string[]
  summary: string
  suggested_location: string
  top_contributors: TopContributorsTypeAlgolia[]
  updated_at: number
  url: string
}

export interface ChapterTypeGraphQL {
  geoLocation: GeoLocation
  isActive: boolean
  key: string
  name: string
  region: string
  relatedUrls: string[]
  summary: string
  suggestedLocation: string
  updatedAt: number
  url: string
}

export interface GeoLocation {
  lat: number
  lng: number
}

export interface GeoLocDataAlgolia {
  _geoloc: { lat: number; lng: number }
  key: string
  name: string
}

export interface GeoLocDataGraphQL {
  geoLocation: GeoLocation
  key: string
  name: string
}
