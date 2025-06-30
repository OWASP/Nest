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

const GITHUB_AUTH_MUTATION = gql`
  mutation GitHubAuth($accessToken: String!) {
    githubAuth(accessToken: $accessToken) {
      authUser {
        username
        role
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
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
        } catch (error) {
          throw new Error('GitHub authentication failed')
        }
      }
      return true
    },

    async jwt({ token, account, user }) {
      if (account?.access_token) {
        token.accessToken = account.access_token

        // Fetch user data including role from GraphQL
        try {
          const { data } = await apolloClient.mutate({
            mutation: GITHUB_AUTH_MUTATION,
            variables: {
              accessToken: account.access_token,
            },
          })

          if (data?.githubAuth?.authUser) {
            token.username = data.githubAuth.authUser.username
            token.role = data.githubAuth.authUser.role
          }
        } catch (error) {
          console.error('Failed to fetch user data:', error)
        }
      }
      return token
    },

    async session({ session, token }) {
      if (token?.accessToken) {
        session.accessToken = token.accessToken
      }
      if (token?.role) {
        session.user.role = token.role
      }
      if (token?.username) {
        session.user.username = token.username
      }

      return session
    },
  },
  secret: NEXTAUTH_SECRET,
  url: NEXTAUTH_URL,
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
