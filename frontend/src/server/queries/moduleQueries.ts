import { gql } from '@apollo/client'

export const GET_MODULES_BY_PROGRAM = gql`
  query ModulesByProgram($programKey: String!) {
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
        githubUser {
          id
          login
          avatarUrl
        }
      }
    }
  }
`

export const GET_MODULE_BY_ID = gql`
  query GetModule($moduleKey: String!, $programKey: String!) {
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
        login
        name
        avatarUrl
      }
    }
  }
`

export const GET_PROGRAM_ADMINS_AND_MODULES = gql`
  query GetProgramAndModules($programKey: String!, $moduleKey: String!) {
    getProgram(programKey: $programKey) {
      id
      admins {
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
      projectId
      projectName
      domains
      experienceLevel
      startedAt
      endedAt
      mentors {
        login
        name
        avatarUrl
      }
    }
  }
`
