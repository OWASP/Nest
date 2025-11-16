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
      labels
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
      labels
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
