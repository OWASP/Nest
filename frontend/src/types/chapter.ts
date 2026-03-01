import type { Contributor } from 'types/contributor'
import type { Leader } from 'types/leader'

export type Chapter = {
  _geoloc?: GeoLocation
  contributionData?: Record<string, number>
  contributionStats?: {
    commits: number
    issues: number
    pullRequests: number
    releases: number
    total: number
  }
  createdAt?: string
  entityLeaders?: Leader[]
  geoLocation?: GeoLocation | null
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
  updatedAt?: string
  url?: string
}

export type GeoLocation = {
  lat: number
  lng: number
}
