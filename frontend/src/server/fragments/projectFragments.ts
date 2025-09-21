import { gql } from '@apollo/client'

export const CONTRIBUTOR_FIELDS = gql`
  fragment ContributorFields on RepositoryContributorNode {
    id
    avatarUrl
    login
    name
  }
`

export const MILESTONE_METADATA_FIELDS = gql`
  fragment MilestoneMetadataFields on MilestoneNode {
    id
    title
    url
    body
    progress
    state
  }
`

export const PROJECT_METADATA_FIELDS = gql`
  ${MILESTONE_METADATA_FIELDS}
  fragment ProjectMetadataFields on ProjectNode {
    id
    contributorsCount
    forksCount
    issuesCount
    name
    starsCount
    summary
    recentMilestones(limit: 25) {
      ...MilestoneMetadataFields
    }
  }
`
