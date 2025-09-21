import { gql } from '@apollo/client'

export const LEADER_FIELDS = gql`
  fragment LeaderFields on UserNode {
    id
    avatarUrl
    company
    location
    login
    name
  }
`
