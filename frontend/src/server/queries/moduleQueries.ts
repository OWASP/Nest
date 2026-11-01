import { gql } from '@apollo/client'

export const GET_MODULES_BY_PROGRAM = gql`
  query GetModulesByProgram($programKey: String!) {
    getProgramModules(programKey: $programKey) {
      id
      key
      name
      description
      experienceLevel
      order
      startedAt
      endedAt
      projectId
      projectName
      mentors {
        id
        login
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

export const GET_MODULE_BY_ID = gql`
  query GetModuleByID($moduleKey: String!, $programKey: String!) {
    getModule(moduleKey: $moduleKey, programKey: $programKey) {
      id
      key
      name
      description
      tags
      domains
      experienceLevel
      startedAt
      endedAt
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

const PROGRAM_ADMINS_AND_SCHEDULE = gql`
  fragment ProgramAdminsAndSchedule on ProgramNode {
    id
    startedAt
    endedAt
    admins {
      id
      login
      name
      avatarUrl
    }
  }
`

const MODULE_DETAIL_WITH_RECENT_PRS = gql`
  fragment ModuleDetailWithRecentPrs on ModuleNode {
    id
    key
    name
    description
    tags
    labels
    projectId
    projectName
    domains
    experienceLevel
    userRole
    menteeCanManageDeadlines
    startedAt
    endedAt
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
    recentPullRequests(limit: $limit, offset: $offset) {
      id
      title
      url
      state
      createdAt
      mergedAt
      organizationName
      repositoryName
      author {
        id
        login
        name
        avatarUrl
      }
    }
  }
`

export const GET_MANAGEMENT_PROGRAM_ADMINS_AND_MODULES = gql`
  query GetManagementProgramAdminsAndModules(
    $programKey: String!
    $moduleKey: String!
    $limit: Int = 4
    $offset: Int = 0
  ) {
    managementProgram(programKey: $programKey) {
      ...ProgramAdminsAndSchedule
    }
    managementModule(moduleKey: $moduleKey, programKey: $programKey) {
      ...ModuleDetailWithRecentPrs
    }
  }
  ${PROGRAM_ADMINS_AND_SCHEDULE}
  ${MODULE_DETAIL_WITH_RECENT_PRS}
`

export const GET_PROGRAM_ADMINS_AND_MODULES = gql`
  query GetProgramAdminsAndModules(
    $programKey: String!
    $moduleKey: String!
    $limit: Int = 4
    $offset: Int = 0
  ) {
    getProgram(programKey: $programKey) {
      ...ProgramAdminsAndSchedule
    }
    getModule(moduleKey: $moduleKey, programKey: $programKey) {
      ...ModuleDetailWithRecentPrs
    }
  }
  ${PROGRAM_ADMINS_AND_SCHEDULE}
  ${MODULE_DETAIL_WITH_RECENT_PRS}
`

const MODULE_ISSUES_LIST = gql`
  fragment ModuleIssuesList on ModuleNode {
    name
    userRole
    issuesCount(label: $label)
    availableLabels
    issues(limit: $limit, offset: $offset, label: $label) {
      id
      number
      title
      state
      isMerged
      labels
      taskDeadline
      assignees {
        avatarUrl
        login
        name
      }
    }
  }
`

export const GET_MANAGEMENT_MODULE_ISSUES = gql`
  query GetManagementModuleIssues(
    $programKey: String!
    $moduleKey: String!
    $limit: Int = 20
    $offset: Int = 0
    $label: String
  ) {
    managementModule(moduleKey: $moduleKey, programKey: $programKey) {
      ...ModuleIssuesList
    }
  }
  ${MODULE_ISSUES_LIST}
`

export const GET_MODULE_ISSUES = gql`
  query GetModuleIssues(
    $programKey: String!
    $moduleKey: String!
    $limit: Int = 20
    $offset: Int = 0
    $label: String
  ) {
    getModule(moduleKey: $moduleKey, programKey: $programKey) {
      ...ModuleIssuesList
    }
  }
  ${MODULE_ISSUES_LIST}
`
