import type { TypedDocumentNode } from '@graphql-typed-document-node/core'
import NextAuth, { type AuthOptions } from 'next-auth'
import GitHubProvider from 'next-auth/providers/github'
import { apolloClient } from 'server/apolloClient'
import { IsChapterLeaderDocument } from 'types/__generated__/chapterQueries.generated'
import {
  IsAdminDocument,
  IsMenteeDocument,
  IsMentorDocument,
  IsProjectLeaderDocument,
} from 'types/__generated__/mentorshipQueries.generated'
import { ExtendedProfile, ExtendedSession } from 'types/auth'
import { IS_GITHUB_AUTH_ENABLED, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET } from 'utils/env.server'

// Shared login-time role check: run the query and extract the boolean, wrapping
// failures with a role-specific message so query options and error handling stay
// in one place for all roles.
async function checkRole<TData>(
  document: TypedDocumentNode<TData, { login: string }>,
  login: string,
  getValue: (data: TData | null | undefined) => boolean,
  roleLabel: string
): Promise<boolean> {
  try {
    const client = await apolloClient
    const { data } = await client.query({
      query: document,
      variables: { login },
      fetchPolicy: 'no-cache',
    })
    return getValue(data)
  } catch (err) {
    throw new Error(
      `Failed to fetch ${roleLabel} status: ${err instanceof Error ? err.message : String(err)}`,
      { cause: err }
    )
  }
}

const checkIfProjectLeader = (login: string) =>
  checkRole(
    IsProjectLeaderDocument,
    login,
    (data) => data?.isProjectLeader ?? false,
    'project leader'
  )

const checkIfChapterLeader = (login: string) =>
  checkRole(
    IsChapterLeaderDocument,
    login,
    (data) => data?.isChapterLeader ?? false,
    'chapter leader'
  )

// A failed chapter leader lookup is retried on later session reads, at most this often.
const CHAPTER_LEADER_RETRY_INTERVAL_MS = 5 * 60 * 1000

const checkIfAdmin = (login: string) =>
  checkRole(IsAdminDocument, login, (data) => data?.isAdmin ?? false, 'program admin')

const checkIfMentor = (login: string) =>
  checkRole(IsMentorDocument, login, (data) => data?.isMentor ?? false, 'mentor')

const checkIfMentee = (login: string) =>
  checkRole(IsMenteeDocument, login, (data) => data?.isMentee ?? false, 'mentee')

const providers = []

if (IS_GITHUB_AUTH_ENABLED) {
  providers.push(
    GitHubProvider({
      clientId: GITHUB_CLIENT_ID!,
      clientSecret: GITHUB_CLIENT_SECRET!,
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

        const [isLeader, isChapterLeader, isAdmin, isMentor, isMentee] = await Promise.all([
          checkIfProjectLeader(login),
          // A failed lookup leaves the flag unset so the next session refresh retries it
          // instead of failing sign-in.
          checkIfChapterLeader(login).catch((err) => {
            // eslint-disable-next-line no-console
            console.warn('Failed to fetch chapter leader status during sign-in:', err)
            return undefined
          }),
          checkIfAdmin(login),
          checkIfMentor(login),
          checkIfMentee(login),
        ])
        token.isLeader = isLeader
        token.isChapterLeader = isChapterLeader
        token.isAdmin = isAdmin
        token.isMentor = isMentor
        token.isMentee = isMentee
        token.chapterLeaderRetryAt =
          isChapterLeader === undefined ? Date.now() + CHAPTER_LEADER_RETRY_INTERVAL_MS : undefined
      } else if (
        token.login &&
        typeof token.isChapterLeader !== 'boolean' &&
        Date.now() >= ((token.chapterLeaderRetryAt as number | undefined) ?? 0)
      ) {
        try {
          token.isChapterLeader = await checkIfChapterLeader(token.login as string)
          token.chapterLeaderRetryAt = undefined
        } catch (err) {
          token.chapterLeaderRetryAt = Date.now() + CHAPTER_LEADER_RETRY_INTERVAL_MS
          // eslint-disable-next-line no-console
          console.warn('Failed to fetch chapter leader status; will retry later:', err)
        }
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
        extSession.user!.isAdmin = token.isAdmin as boolean
        extSession.user!.isMentor = token.isMentor as boolean
        extSession.user!.isMentee = token.isMentee as boolean
        extSession.user!.isLeader = token.isLeader as boolean
        extSession.user!.isChapterLeader = token.isChapterLeader as boolean
        extSession.user!.isOwaspStaff = token.isOwaspStaff as boolean
      }
      return session
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
