import { gql } from '@apollo/client'

export const UPDATE_PROGRAM = gql`
  mutation UpdateProgram($input: UpdateProgramInput!) {
    updateProgram(inputData: $input) {
      key
      name
      description
      status
      menteesLimit
      experienceLevels
      startedAt
      endedAt
      tags
      domains
      admins {
        login
      }
    }
  }
`

export const CREATE_PROGRAM = gql`
  mutation CreateProgram($input: CreateProgramInput!) {
    createProgram(inputData: $input) {
      id
      key
      name
      description
      menteesLimit
      startedAt
      endedAt
      experienceLevels
      tags
      domains
      status
      admins {
        login
        name
        avatarUrl
      }
    }
  }
`

export const UPDATE_PROGRAM_STATUS_MUTATION = gql`
  mutation updateProgramStatus($inputData: UpdateProgramStatusInput!) {
    updateProgramStatus(inputData: $inputData) {
      key
      status
    }
  }
`
