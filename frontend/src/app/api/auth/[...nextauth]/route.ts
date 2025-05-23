import { gql } from '@apollo/client'
import NextAuth from 'next-auth'
import GitHubProvider from 'next-auth/providers/github'
import { apolloClient } from 'server/apolloClient'
import { GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET } from 'utils/credentials'

export const authOptions = {
  providers: [
    GitHubProvider({
      clientId: GITHUB_CLIENT_ID!,
      clientSecret: GITHUB_CLIENT_SECRET!,
    }),
  ],
  session: {
    strategy: 'jwt' as const,
  },
  callbacks: {
    async signIn({ account }) {
      if (account?.provider === 'github' && account.access_token) {
        try {
          const { data } = await apolloClient.mutate({
            mutation: gql`
              mutation GitHubAuth($accessToken: String!) {
                githubAuth(accessToken: $accessToken) {
                  authUser {
                    username
                  }
                }
              }
            `,
            variables: {
              accessToken: account.access_token,
            },
          })
          if (!data.githubAuth.authUser) throw new Error('User sync failed')
          return true
        } catch (error) {
          console.error('GitHub authentication failed:', error)
          return false
        }
      }
      return true
    },

    async jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token
      }
      return token
    },

    async session({ session, token }) {
      session.accessToken = token.accessToken
      return session
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
