import type { Contributor } from 'types/contributor'
import type { Leader } from 'types/leader'

export type Chapter = {
  _geoloc?: GeoLocation
  createdAt?: number
  entityLeaders?: Leader[]
  geoLocation?: GeoLocation
  isActive?: boolean
  key: string
  leaders?: string[]
  name: string
  objectID?: string
  region?: string
  relatedUrls?: string[]
  suggestedLocation: string
  summary?: string
  topContributors?: Contributor[]
  updatedAt?: number
  url?: string
}

export type GeoLocation = {
  lat: number
  lng: number
}
