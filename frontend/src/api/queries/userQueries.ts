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
    location
    login
    name
    publicRepositoriesCount
    url
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
  }
}
`
