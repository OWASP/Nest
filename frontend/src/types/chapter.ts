import { TopContributors } from 'types/contributor'

export type Chapter = {
  _geoloc?: { lat: number; lng: number }
  createdAt: number
  geoLocation?: { lat: number; lng: number }
  isActive: boolean
  key: string
  leaders: string[]
  name: string
  objectID: string
  region: string
  relatedUrls: string[]
  suggestedLocation: string
  summary: string
  topContributors: TopContributors[]
  updatedAt: number
  url: string
}

export type GeoLocation = {
  lat: number
  lng: number
}

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
