import type { AuthOptions } from 'next-auth'
import NextAuth from 'next-auth'
import { apolloClient } from 'server/apolloClient'
import { IsChapterLeaderDocument } from 'types/__generated__/chapterQueries.generated'
import {
  IsMenteeDocument,
  IsMentorDocument,
  IsProjectLeaderDocument,
} from 'types/__generated__/mentorshipQueries.generated'
import 'app/api/auth/[...nextauth]/route'

jest.mock('next-auth', () => ({
  __esModule: true,
  default: jest.fn(() => jest.fn()),
}))

jest.mock('next-auth/providers/github', () => ({
  __esModule: true,
  default: jest.fn(() => ({ id: 'github' })),
}))

jest.mock('server/apolloClient', () => ({
  apolloClient: { query: jest.fn() },
}))

jest.mock('utils/env.server', () => ({
  GITHUB_CLIENT_ID: 'client-id',
  GITHUB_CLIENT_SECRET: 'client-secret',
  IS_GITHUB_AUTH_ENABLED: true,
}))

type JwtCallback = NonNullable<NonNullable<AuthOptions['callbacks']>['jwt']>
type JwtParams = Parameters<JwtCallback>[0]

const mockQuery = apolloClient.query as jest.Mock
const authOptions = (NextAuth as unknown as jest.Mock).mock.calls[0][0] as AuthOptions
const jwt = authOptions.callbacks!.jwt! as (params: Partial<JwtParams>) => ReturnType<JwtCallback>

const roleResponses = new Map<unknown, Record<string, boolean>>([
  [IsProjectLeaderDocument, { isProjectLeader: true }],
  [IsChapterLeaderDocument, { isChapterLeader: true }],
  [IsMentorDocument, { isMentor: false }],
  [IsMenteeDocument, { isMentee: true }],
])

const resolveRoles = (failing: unknown[] = []) =>
  mockQuery.mockImplementation(({ query }: { query: unknown }) =>
    failing.includes(query)
      ? Promise.reject(new Error('Backend unavailable'))
      : Promise.resolve({ data: roleResponses.get(query) })
  )

describe('NextAuth route jwt callback', () => {
  let warnSpy: jest.SpyInstance

  beforeEach(() => {
    warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {})
  })

  afterEach(() => {
    warnSpy.mockRestore()
    jest.clearAllMocks()
  })

  it('resolves every role flag on sign-in', async () => {
    resolveRoles()

    const token = await jwt({
      token: {},
      // eslint-disable-next-line @typescript-eslint/naming-convention
      account: { access_token: 'gh-token' } as unknown as JwtParams['account'],
      profile: { login: 'testuser' } as unknown as JwtParams['profile'],
    })

    expect(token).toMatchObject({
      accessToken: 'gh-token',
      isChapterLeader: true,
      isLeader: true,
      isMentee: true,
      isMentor: false,
      login: 'testuser',
    })
    expect(mockQuery).toHaveBeenCalledWith(
      expect.objectContaining({ variables: { login: 'testuser' }, fetchPolicy: 'no-cache' })
    )
  })

  it('completes sign-in when the chapter leader lookup fails', async () => {
    resolveRoles([IsChapterLeaderDocument])

    const token = await jwt({
      token: {},
      profile: { login: 'testuser' } as unknown as JwtParams['profile'],
    })

    expect(token.isLeader).toBe(true)
    expect(token.isChapterLeader).toBeUndefined()
    expect(warnSpy).toHaveBeenCalled()
  })

  it('still fails sign-in when another role lookup fails', async () => {
    resolveRoles([IsProjectLeaderDocument])

    await expect(
      jwt({ token: {}, profile: { login: 'testuser' } as unknown as JwtParams['profile'] })
    ).rejects.toThrow('Failed to fetch project leader status')
  })

  it('retries the chapter leader lookup for a token missing the flag', async () => {
    resolveRoles()

    const token = await jwt({ token: { login: 'testuser', isLeader: false } })

    expect(token.isChapterLeader).toBe(true)
    expect(mockQuery).toHaveBeenCalledTimes(1)
    expect(mockQuery).toHaveBeenCalledWith(
      expect.objectContaining({ query: IsChapterLeaderDocument })
    )
  })

  it('leaves the flag unset when the retry fails', async () => {
    resolveRoles([IsChapterLeaderDocument])

    const token = await jwt({ token: { login: 'testuser' } })

    expect(token.isChapterLeader).toBeUndefined()
    expect(warnSpy).toHaveBeenCalledWith(
      'Failed to fetch chapter leader status; will retry on next session refresh:',
      expect.any(Error)
    )
  })

  it('does not query again once the flag is set', async () => {
    const token = await jwt({ token: { login: 'testuser', isChapterLeader: false } })

    expect(token.isChapterLeader).toBe(false)
    expect(mockQuery).not.toHaveBeenCalled()
  })
})
