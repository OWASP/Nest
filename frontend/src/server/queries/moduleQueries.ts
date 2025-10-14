import { gql } from '@apollo/client'

export const GET_MODULES_BY_PROGRAM = gql`
  query GetModulesByProgram($programKey: String!) {
    getProgramModules(programKey: $programKey) {
      id
      key
      name
      description
      experienceLevel
      startedAt
      endedAt
      projectId
      projectName
      mentors {
        id
        login
        avatarUrl
      }
    }
  }
`

export const GET_MODULE_BY_ID = gql`
  query GetModuleByID($moduleKey: String!, $programKey: String!) {
    getModule(moduleKey: $moduleKey, programKey: $programKey) {
      id
      key
      name
      description
      tags
      domains
      experienceLevel
      startedAt
      endedAt
      mentors {
        id
        login
        name
        avatarUrl
      }
    }
  }
`

export const GET_PROGRAM_ADMINS_AND_MODULES = gql`
  query GetProgramAdminsAndModules($programKey: String!, $moduleKey: String!) {
    getProgram(programKey: $programKey) {
      id
      admins {
        id
        login
        name
        avatarUrl
      }
    }
    getModule(moduleKey: $moduleKey, programKey: $programKey) {
      id
      key
      name
      description
      tags
      labels
      projectId
      projectName
      domains
      experienceLevel
      startedAt
      endedAt
      mentors {
        id
        login
        name
        avatarUrl
      }
    }
  }
`

export const GET_MODULE_ISSUES = gql`
  query GetModuleIssues(
    $programKey: String!
    $moduleKey: String!
    $limit: Int = 20
    $offset: Int = 0
    $label: String
  ) {
    getModule(moduleKey: $moduleKey, programKey: $programKey) {
      name
      issuesCount(label: $label)
      availableLabels
      issues(limit: $limit, offset: $offset, label: $label) {
        id
        number
        title
        state
        labels
        assignees {
          avatarUrl
          login
          name
        }
      }
    }
  }
`
