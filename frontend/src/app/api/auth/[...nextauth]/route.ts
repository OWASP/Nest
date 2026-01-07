import NextAuth, { type AuthOptions, type Profile } from 'next-auth'
import GitHubProvider, { type GithubProfile } from 'next-auth/providers/github'
import { apolloClient } from 'server/apolloClient'
import {
  IsMentorDocument,
  IsProjectLeaderDocument,
} from 'types/__generated__/mentorshipQueries.generated'
import { ExtendedSession } from 'types/auth'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/env.server'

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

// Fixed: Explicitly typed the providers array to avoid 'never' or 'any' issues
const providers: AuthOptions['providers'] = []

if (IS_GITHUB_AUTH_ENABLED) {
  providers.push(
    GitHubProvider({
      clientId: process.env.NEXT_SERVER_GITHUB_CLIENT_ID || '',
      clientSecret: process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET || '',
      profile(profile: GithubProfile) {
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

      const extendedProfile = profile as (Profile & { login?: string })
      if (extendedProfile?.login) {
        const login = extendedProfile.login
        token.login = login

        const isLeader = await checkIfProjectLeader(login)
        const isMentor = await checkIfMentor(login)
        token.isLeader = isLeader
        token.isMentor = isMentor
      }

      if (trigger === 'update' && session) {
        const extendedSession = session as ExtendedSession
        token.isOwaspStaff = extendedSession.user?.isOwaspStaff || false
      }
      return token
    },

    async session({ session, token }) {
      const extendedSession = session as ExtendedSession
      extendedSession.accessToken = token.accessToken as string

      if (extendedSession.user) {
        extendedSession.user.login = token.login as string
        extendedSession.user.isMentor = token.isMentor as boolean
        extendedSession.user.isLeader = token.isLeader as boolean
        extendedSession.user.isOwaspStaff = token.isOwaspStaff as boolean
      }
      return extendedSession
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }