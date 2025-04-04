import { TopContributorsTypeAlgolia, TopContributorsTypeGraphql } from './contributor'

export interface ChapterDataType {
  active_committees_count: number
  chapters: ChapterTypeAlgolia[]
  total_pages: number
}

export interface ChapterTypeAlgolia {
  _geoloc: [number, number]
  created_at: number
  is_active: boolean
  key: string
  leaders: string[]
  name: string
  objectID: string
  region: string
  related_urls: string[]
  suggested_location: string
  summary: string
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
  topContributors: TopContributorsTypeGraphql[]
  updatedAt: number
  url: string
}

export interface GeoLocation {
  lat: number
  lng: number
}

export interface GeoLocDataAlgolia {
  _geoloc: [number, number]
  key: string
  name: string
}

export interface GeoLocDataGraphQL {
  geoLocation: GeoLocation
  key: string
  name: string
}
