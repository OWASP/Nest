import { gql } from '@apollo/client'

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
    user(login: $key) {
      avatarUrl
      bio
      company
      createdAt
      email
      followersCount
      followingCount
      issues {
        title
        number
        createdAt
        commentsCount
        repository {
          key
          ownerKey
        }
      }
      issuesCount
      location
      login
      name
      publicRepositoriesCount
      releases {
        name
        tagName
        publishedAt
        isPreRelease
        repository {
          key
          ownerKey
        }
      }
      releasesCount
      url
    }
  }
`
