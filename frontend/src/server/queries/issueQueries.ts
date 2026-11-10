import { gql } from '@apollo/client'

const MODULE_ISSUE_VIEW_FIELDS = gql`
  fragment ModuleIssueViewFields on ModuleNode {
    id
    userRole
    menteeCanManageDeadlines
    startedAt
    endedAt
    taskDeadline(issueId: $issueId)
    taskAssignedAt(issueId: $issueId)
    issueById(issueId: $issueId) {
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
    interestedUsers(issueId: $issueId) {
      id
      login
      name
      avatarUrl
    }
    issueMentees(issueId: $issueId) {
      id
      login
      name
      avatarUrl
    }
  }
`

export const GET_MANAGEMENT_MODULE_ISSUE_VIEW = gql`
  query GetManagementModuleIssueView(
    $programKey: String!
    $moduleKey: String!
    $issueId: ID!
    $limit: Int = 4
    $offset: Int = 0
  ) {
    managementModule(moduleKey: $moduleKey, programKey: $programKey) {
      ...ModuleIssueViewFields
    }
  }
  ${MODULE_ISSUE_VIEW_FIELDS}
`

export const GET_MODULE_ISSUE_VIEW = gql`
  query GetModuleIssueView(
    $programKey: String!
    $moduleKey: String!
    $issueId: ID!
    $limit: Int = 4
    $offset: Int = 0
  ) {
    getModule(programKey: $programKey, moduleKey: $moduleKey) {
      ...ModuleIssueViewFields
    }
  }
  ${MODULE_ISSUE_VIEW_FIELDS}
`

export const ASSIGN_ISSUE_TO_USER = gql`
  mutation AssignIssueToUser(
    $programKey: String!
    $moduleKey: String!
    $issueId: ID!
    $userLogin: String!
  ) {
    assignIssueToUser(
      programKey: $programKey
      moduleKey: $moduleKey
      issueId: $issueId
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
    $issueId: ID!
    $userLogin: String!
  ) {
    unassignIssueFromUser(
      programKey: $programKey
      moduleKey: $moduleKey
      issueId: $issueId
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
    $issueId: ID!
    $deadlineAt: DateTime!
  ) {
    setTaskDeadline(
      programKey: $programKey
      moduleKey: $moduleKey
      issueId: $issueId
      deadlineAt: $deadlineAt
    ) {
      id
    }
  }
`

export const CLEAR_TASK_DEADLINE = gql`
  mutation ClearTaskDeadline($programKey: String!, $moduleKey: String!, $issueId: ID!) {
    clearTaskDeadline(programKey: $programKey, moduleKey: $moduleKey, issueId: $issueId) {
      id
    }
  }
`
