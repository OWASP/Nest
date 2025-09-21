import { gql } from '@apollo/client'
import { CHAPTER_FIELDS, CHAPTER_METADATA_FIELDS } from 'server/fragments/chapterFragments'
import { CONTRIBUTOR_FIELDS } from 'server/fragments/projectFragments'

export const GET_CHAPTER_DATA = gql`
  ${CONTRIBUTOR_FIELDS}
  ${CHAPTER_FIELDS}
  query GetChapterData($key: String!) {
    chapter(key: $key) {
      ...ChapterFields
    }
    topContributors(chapter: $key) {
      ...ContributorFields
    }
  }
`

export const GET_CHAPTER_METADATA = gql`
  ${CHAPTER_METADATA_FIELDS}
  query GetChapterMetadata($key: String!) {
    chapter(key: $key) {
      ...ChapterMetadataFields
    }
  }
`
