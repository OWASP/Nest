import { gql } from '@apollo/client'

export const GET_MODULES_BY_PROGRAM = gql`
  query ModulesByProgram($programId: ID!) {
    modulesByProgram(programId: $programId) {
      id
      name
      description
      experienceLevel
      startedAt
      endedAt
      projectId
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
  query GetModule($id: ID!) {
    getModule(id: $id) {
      id
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

export const UPDATE_MODULE = gql`
  mutation UpdateModule($input: UpdateModuleInput!) {
    updateModule(input: $input) {
      id
      name
      description
      experienceLevel
      startedAt
      endedAt
      tags
      domains
      projectId
      mentors {
        login
        name
        avatarUrl
      }
    }
  }
`

export const CREATE_MODULE = gql`
  mutation CreateModule($input: CreateModuleInput!) {
    createModule(input: $input) {
      id
      name
      description
      experienceLevel
      startedAt
      endedAt
      domains
      tags
      projectId
      mentors {
        login
        name
        avatarUrl
      }
    }
  }
`
