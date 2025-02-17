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
        commentsCount
        createdAt
        number
        repository {
          key
          ownerKey
        }
        title
      }
      issuesCount
      location
      login
      name
      publicRepositoriesCount
      releases {
        isPreRelease
        name
        publishedAt
        repository {
          key
          ownerKey
        }
        tagName
      }
      releasesCount
      url
    }
  }
`
