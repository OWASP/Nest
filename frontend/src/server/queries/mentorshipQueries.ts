import { gql } from '@apollo/client'

export const APPLY_AS_MENTEE = gql`
  mutation ApplyAsMentee {
    applyAsMentee {
      success
      message
      user {
        username
      }
    }
  }
`

export const APPLY_AS_MENTOR = gql`
  mutation ApplyAsMentor {
    applyAsMentor {
      success
      message
      user {
        username
      }
    }
  }
`
