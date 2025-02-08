import { gql } from '@apollo/client'

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
    user(key: $key) {
      avatar_url
      bio
      company
      created_at
      email
      followers_count
      following_count
      location
      login
      name
      public_repositories_count
      url
      issues {
        title
        number
        created_at
        comments_count
        repository {
          key
          owner_key
        }
      }
      issues_count
      releases {
        name
        tag_name
        published_at
        is_pre_release
        repository {
          key
          owner_key
        }
      }
      releases_count
    }
  }
`