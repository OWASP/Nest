import { TopContributorsType } from 'types/contributor'

export interface ChapterDataType {
  active_committees_count: number
  chapters: ChapterType[]
  total_pages: number
}

export interface ChapterType {
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

// export interface ChapterTypeGraphQL {
//   geoLocation: GeoLocation
//   isActive: boolean
//   key: string
//   name: string
//   region: string
//   relatedUrls: string[]
//   summary: string
//   suggestedLocation: string
//   updatedAt: number
//   url: string
// }

// export interface GeoLocation {
//   lat: number
//   lng: number
// }

// export interface GeoLocDataAlgolia {
//   _geoloc: { lat: number; lng: number }
//   key: string
//   name: string
// }

// export interface GeoLocDataGraphQL {
//   geoLocation: { lat: number; lng: number }
//   key: string
//   name: string
// }
