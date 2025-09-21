import { gql } from '@apollo/client'

export const CHAPTER_MAP_FIELDS = gql`
  fragment ChapterMapFields on ChapterNode {
    key
    name
    geoLocation {
      lat
      lng
    }
  }
`

export const CHAPTER_METADATA_FIELDS = gql`
  fragment ChapterMetadataFields on ChapterNode {
    id
    name
    summary
  }
`

export const CHAPTER_FIELDS = gql`
  ${CHAPTER_METADATA_FIELDS}
  ${CHAPTER_MAP_FIELDS}
  fragment ChapterFields on ChapterNode {
    ...ChapterMetadataFields
    ...ChapterMapFields
    isActive
    region
    relatedUrls
    suggestedLocation
    updatedAt
    url
  }
`
