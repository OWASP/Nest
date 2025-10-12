import { gql } from '@apollo/client'

export const GET_MODULE_ISSUE_VIEW = gql`
  query GetModuleIssueView($programKey: String!, $moduleKey: String!, $number: Int!) {
    getModule(programKey: $programKey, moduleKey: $moduleKey) {
      id
      taskDeadline(issueNumber: $number)
      taskAssignedAt(issueNumber: $number)
      issueByNumber(number: $number) {
        id
        number
        title
        summary
        url
        state
        createdAt
        organizationName
        repositoryName
        author {
          id
          login
          name
          avatarUrl
        }
        assignees {
          id
          login
          name
          avatarUrl
        }
        labels
        pullRequests {
          id
          title
          url
          state
          createdAt
          mergedAt
          author {
            id
            login
            name
            avatarUrl
          }
        }
      }
      interestedUsers(issueNumber: $number) {
        id
        login
        name
        avatarUrl
      }
    }
  }
`

export const ASSIGN_ISSUE_TO_USER = gql`
  mutation AssignIssueToUser(
    $programKey: String!
    $moduleKey: String!
    $issueNumber: Int!
    $userLogin: String!
  ) {
    assignIssueToUser(
      programKey: $programKey
      moduleKey: $moduleKey
      issueNumber: $issueNumber
      userLogin: $userLogin
    ) {
      id
    }
  }
`

export const UNASSIGN_ISSUE_FROM_USER = gql`
  mutation UnassignIssueFromUser(
    $programKey: String!
    $moduleKey: String!
    $issueNumber: Int!
    $userLogin: String!
  ) {
    unassignIssueFromUser(
      programKey: $programKey
      moduleKey: $moduleKey
      issueNumber: $issueNumber
      userLogin: $userLogin
    ) {
      id
    }
  }
`
