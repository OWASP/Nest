import { gql } from '@apollo/client'

export const GET_MODULES_BY_PROGRAM = gql`
  query ModulesByProgram($programKey: String!) {
    modulesByProgram(programKey: $programKey) {
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
  query GetModule($moduleKey: String!) {
    getModule(moduleKey: $moduleKey) {
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

export const UPDATE_MODULE = gql`
  mutation UpdateModule($input: UpdateModuleInput!) {
    updateModule(inputData: $input) {
      id
      key
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
    createModule(inputData: $input) {
      id
      key
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

export const GET_PROGRAM_ADMINS_AND_MODULES = gql`
  query GetProgramAndModules($programKey: String!, $moduleKey: String!) {
    program(programKey: $programKey) {
      id
      admins {
        login
        name
        avatarUrl
      }
    }
    getModule(moduleKey: $moduleKey) {
      id
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
