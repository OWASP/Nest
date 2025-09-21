import { gql } from '@apollo/client'

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
        id
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
        id
        login
        name
        avatarUrl
      }
    }
  }
`
