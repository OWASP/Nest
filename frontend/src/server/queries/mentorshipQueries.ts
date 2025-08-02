import { gql } from '@apollo/client'

export const IS_PROJECT_LEADER_QUERY = gql`
  query IsProjectLeader($login: String!) {
    isProjectLeader(login: $login)
  }
`
