import NextAuth, { type AuthOptions } from 'next-auth'
import GitHubProvider from 'next-auth/providers/github'
import { ExtendedProfile, ExtendedSession } from 'types/auth'
import {
  GITHUB_CLIENT_ID,
  GITHUB_CLIENT_SECRET,
  IS_GITHUB_AUTH_ENABLED,
  NEXTAUTH_SECRET,
} from 'utils/credentials'

const providers = []

if (IS_GITHUB_AUTH_ENABLED) {
  providers.push(
    GitHubProvider({
      clientId: GITHUB_CLIENT_ID,
      clientSecret: GITHUB_CLIENT_SECRET,
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
        token.login = (profile as ExtendedProfile)?.login
      }
      if (trigger === 'update' && session) {
        token.isOwaspStaff = (session as ExtendedSession).user.isOwaspStaff || false
      }
      return token
    },

    async session({ session, token }) {
      ;(session as ExtendedSession).accessToken = token.accessToken as string
      if (session.user) {
        ;(session as ExtendedSession).user.login = token.login as string
        ;(session as ExtendedSession).user.isOwaspStaff = token.isOwaspStaff as boolean
      }
      return session
    },
  },
  secret: NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
