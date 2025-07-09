import { gql } from '@apollo/client'
import NextAuth from 'next-auth'
import GitHubProvider from 'next-auth/providers/github'
import { apolloClient } from 'server/apolloClient'
import {
  GITHUB_CLIENT_ID,
  GITHUB_CLIENT_SECRET,
  IS_GITHUB_AUTH_ENABLED,
  NEXTAUTH_SECRET,
  NEXTAUTH_URL,
} from 'utils/credentials'

const providers = []

if (IS_GITHUB_AUTH_ENABLED) {
  providers.push(
    GitHubProvider({
      clientId: GITHUB_CLIENT_ID,
      clientSecret: GITHUB_CLIENT_SECRET,
    })
  )
}

export const GET_USER_ROLES = gql`
  query GetUserRoles($accessToken: String!) {
    currentUserRoles(accessToken: $accessToken) {
      roles
    }
  }
`


const GITHUB_AUTH_MUTATION = gql`
  mutation GitHubAuth($accessToken: String!) {
    githubAuth(accessToken: $accessToken) {
      authUser {
        username
      }
    }
  }
`

const authOptions = {
  providers,
  session: {
    strategy: 'jwt' as const,
  },
  callbacks: {
    async signIn({ account }) {
      if (account?.provider === 'github' && account.access_token) {
        try {
          const { data } = await apolloClient.mutate({
            mutation: GITHUB_AUTH_MUTATION,
            variables: {
              accessToken: account.access_token,
            },
          })
          if (!data?.githubAuth?.authUser) throw new Error('User sync failed')
          return true
        } catch (error) {
          throw new Error('GitHub authentication failed')
        }
      }
      return true
    },

    async jwt({ token, account, profile }) {
      if (account?.access_token) {
        token.accessToken = account.access_token
      }

      if (profile) {
        token.login = profile.login
      }

      if (token?.accessToken) {
        try {
          const { data } = await apolloClient.query({
            query: GET_USER_ROLES,
            variables: {
              accessToken: token.accessToken,
            },
          })

          token.roles = data?.currentUserRoles?.roles ?? []
          console.log(token.roles)
        } catch (error) {
          console.error('GitHub role fetch failed:', error)
          token.roles = []
        }
      }

      return token
    },

    async session({ session, token }) {
      if (token?.accessToken) {
        session.accessToken = token.accessToken
      }
      if (token?.roles) {
        session.user.roles = token.roles
      }

      return session
    },
  },
  secret: NEXTAUTH_SECRET,
  url: NEXTAUTH_URL,
}


const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
