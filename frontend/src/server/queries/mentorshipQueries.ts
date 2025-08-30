import { gql } from '@apollo/client'

export const IS_PROJECT_LEADER_QUERY = gql`
  query IsProjectLeader($login: String!) {
    isProjectLeader(login: $login)
  }
`

export const IS_MENTOR_QUERY = gql`
  query IsMentor($login: String!) {
    isMentor(login: $login)
  }
`
