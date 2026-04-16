import { gql } from '@apollo/client'

export const GET_MODULE_ISSUE_VIEW = gql`
  query GetModuleIssueView(
    $programKey: String!
    $moduleKey: String!
    $number: Int!
    $limit: Int = 4
    $offset: Int = 0
  ) {
    getModule(programKey: $programKey, moduleKey: $moduleKey) {
      id
      taskDeadline(issueNumber: $number)
      taskAssignedAt(issueNumber: $number)
      issueByNumber(number: $number) {
        id
        number
        title
        body
        url
        state
        isMerged
        organizationName
        repositoryName
        assignees {
          id
          login
          name
          avatarUrl
        }
        labels
        pullRequests(limit: $limit, offset: $offset) {
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
      issueMentees(issueNumber: $number) {
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

export const SET_TASK_DEADLINE = gql`
  mutation SetTaskDeadline(
    $programKey: String!
    $moduleKey: String!
    $issueNumber: Int!
    $deadlineAt: DateTime!
  ) {
    setTaskDeadline(
      programKey: $programKey
      moduleKey: $moduleKey
      issueNumber: $issueNumber
      deadlineAt: $deadlineAt
    ) {
      id
    }
  }
`

export const CLEAR_TASK_DEADLINE = gql`
  mutation ClearTaskDeadline($programKey: String!, $moduleKey: String!, $issueNumber: Int!) {
    clearTaskDeadline(programKey: $programKey, moduleKey: $moduleKey, issueNumber: $issueNumber) {
      id
    }
  }
`
