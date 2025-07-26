import { gql } from '@apollo/client'

export const IS_PROJECT_LEADER_QUERY = gql`
  query IsProjectLeader {
    isProjectLeader
  }
`
