import type { Contributor } from 'types/contributor'

export type Chapter = {
  _geoloc?: GeoLocation
  createdAt: number
  geoLocation?: GeoLocation
  isActive: boolean
  key: string
  leaders: string[]
  name: string
  objectID: string
  region: string
  relatedUrls: string[]
  suggestedLocation: string
  summary: string
  topContributors: Contributor[]
  updatedAt: number
  url: string
}

export type GeoLocation = {
  lat: number
  lng: number
}
