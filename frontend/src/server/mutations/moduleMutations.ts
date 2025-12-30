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
      mentees {
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
      description
      domains
      endedAt
      experienceLevel
      id
      key
      labels
      name
      projectId
      startedAt
      tags
      mentors {
        avatarUrl
        id
        login
        name
      }
      mentees {
        avatarUrl
        id
        login
        name
      }
    }
  }
`

export const SET_MODULE_ORDER = gql`
  mutation SetModuleOrder($input: SetModuleOrderInput!) {
    setModuleOrder(inputData: $input) {
      id
    }
  }
`
