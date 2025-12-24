import { gql } from '@apollo/client'

export const GET_MODULE_MENTEE_DETAILS = gql`
  query GetModuleMenteeDetails($programKey: String!, $moduleKey: String!, $menteeKey: String!) {
    getMenteeDetails(programKey: $programKey, moduleKey: $moduleKey, menteeKey: $menteeKey) {
      id
      login
      name
      avatarUrl
      bio
      experienceLevel
      domains
      tags
    }
    getMenteeModuleIssues(
      programKey: $programKey
      moduleKey: $moduleKey
      menteeKey: $menteeKey
      limit: 50
    ) {
      id
      number
      title
      state
      labels
      assignees {
        login
        name
        avatarUrl
      }
      createdAt
      url
    }
  }
`
