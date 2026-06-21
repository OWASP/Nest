import { ClaimStatusEnum } from 'types/__generated__/graphql'

export type Claim = {
  __typename?: string
  id: string
  createdAt?: string
  description: string
  key: string
  name: string
  order?: number
  status: ClaimStatusEnum
  updatedAt?: string
}
