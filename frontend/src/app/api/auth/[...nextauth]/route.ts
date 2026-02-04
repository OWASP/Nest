import NextAuth, { type AuthOptions } from 'next-auth'
import GitHubProvider from 'next-auth/providers/github'
import { apolloClient } from 'server/apolloClient'
import {
  IsMentorDocument,
  IsProjectLeaderDocument,
} from 'types/__generated__/mentorshipQueries.generated'
import { ExtendedProfile, ExtendedSession } from 'types/auth'
import { IS_GITHUB_AUTH_ENABLED, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET } from 'utils/env.server'

async function checkIfProjectLeader(login: string): Promise<boolean> {
  try {
    const client = await apolloClient
    const { data } = await client.query({
      query: IsProjectLeaderDocument,
      variables: { login },
      fetchPolicy: 'no-cache',
    })
    return data?.isProjectLeader ?? false
  } catch (err) {
    throw new Error(
      `Failed to fetch project leader status: ${err instanceof Error ? err.message : String(err)}`,
      { cause: err }
    )
  }
}

async function checkIfMentor(login: string): Promise<boolean> {
  try {
    const client = await apolloClient
    const { data } = await client.query({
      query: IsMentorDocument,
      variables: { login },
      fetchPolicy: 'no-cache',
    })
    return data?.isMentor ?? false
  } catch (err) {
    throw new Error(
      `Failed to fetch mentor status: ${err instanceof Error ? err.message : String(err)}`,
      { cause: err }
    )
  }
}

const providers = []

if (IS_GITHUB_AUTH_ENABLED) {
  const githubClientId = GITHUB_CLIENT_ID!
  const githubClientSecret = GITHUB_CLIENT_SECRET!
  providers.push(
    GitHubProvider({
      clientId: githubClientId,
      clientSecret: githubClientSecret,
      profile(profile) {
        return {
          email: profile.email,
          id: profile.id.toString(),
          image: profile.avatar_url,
          login: profile.login,
          name: profile.name,
        }
      },
    })
  )
}

const authOptions: AuthOptions = {
  providers,
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    async signIn({ account }) {
      return Boolean(account?.provider === 'github' && account.access_token)
    },

    async jwt({ token, account, profile, trigger, session }) {
      if (account?.access_token) {
        token.accessToken = account.access_token
      }

      if ((profile as ExtendedProfile)?.login) {
        const login = (profile as ExtendedProfile).login
        token.login = login

        const isLeader = await checkIfProjectLeader(login)
        const isMentor = await checkIfMentor(login)
        token.isLeader = isLeader
        token.isMentor = isMentor
      }

      if (trigger === 'update' && session) {
        const extSession = session as ExtendedSession
        token.isOwaspStaff = extSession.user?.isOwaspStaff || false
      }
      return token
    },

    async session({ session, token }) {
      ;(session as ExtendedSession).accessToken = token.accessToken as string

      if (session?.user) {
        const extSession = session as ExtendedSession
        extSession.user!.login = token.login as string
        extSession.user!.isMentor = token.isMentor as boolean
        extSession.user!.isLeader = token.isLeader as boolean
        extSession.user!.isOwaspStaff = token.isOwaspStaff as boolean
      }
      return session
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
