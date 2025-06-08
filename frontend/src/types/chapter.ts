import { TopContributorsType } from 'types/contributor'

export type ChapterType = {
  _geoloc?: { lat: number; lng: number }
  geoLocation?: { lat: number; lng: number }
  createdAt: number
  isActive: boolean
  key: string
  leaders: string[]
  name: string
  objectID: string
  region: string
  relatedUrls: string[]
  summary: string
  suggestedLocation: string
  topContributors: TopContributorsType[]
  updatedAt: number
  url: string
}

export type GeoLocation = {
  lat: number
  lng: number
}

//todo fix the interfaces
export type GeoLocDataAlgolia = {
  _geoloc: GeoLocation
  key: string
  name: string
}

export type GeoLocDataGraphQL = {
  geoLocation: GeoLocation
  key: string
  name: string
}
