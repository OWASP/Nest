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
    getModule(moduleId: $id) {
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
    updateModule(inputData: $input) {
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
    createModule(inputData: $input) {
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

export const GET_PROGRAM_ADMINS_AND_MODULES = gql`
  query GetProgramAndModules($programId: ID!, $moduleId: ID!) {
    program(programId: $programId) {
      id
      admins {
        login
        name
        avatarUrl
      }
    }
    getModule(moduleId: $moduleId) {
      id
      name
      description
      tags
      projectId
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
