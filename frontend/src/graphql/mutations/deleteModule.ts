import { gql } from '@apollo/client'

export const DELETE_MODULE_MUTATION = gql`
  mutation DeleteModule($programKey: String!, $moduleKey: String!) {
    deleteModule(programKey: $programKey, moduleKey: $moduleKey)
  }
`
