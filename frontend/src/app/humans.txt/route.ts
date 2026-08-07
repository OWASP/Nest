import { NextResponse } from 'next/server'
import { apolloClient } from 'server/apolloClient'
import { GetAboutPageDataDocument } from 'types/__generated__/aboutQueries.generated'

export const revalidate = 86400

const projectKey = 'nest'
const leaders = ['arkid15r', 'kasya', 'mamicidal']
function formatPerson(person?: { name?: string | null; login?: string | null } | null): string {
  if (!person) return ''
  if (person.name && person.login) return `${person.name} (@${person.login})`
  if (person.name) return person.name
  if (person.login) return `@${person.login}`
  return ''
}

export async function GET() {
  try {
    const { data } = await apolloClient.query({
      query: GetAboutPageDataDocument,
      variables: {
        projectKey,
        excludedUsernames: leaders,
        hasFullName: true,
        limit: 24,
        leader1: leaders[0],
        leader2: leaders[1],
        leader3: leaders[2],
      },
    })

    const leadersList = [data?.leader1, data?.leader2, data?.leader3]
      .map(formatPerson)
      .filter(Boolean)

    const contributorsList = (data?.topContributors ?? []).map(formatPerson).filter(Boolean)

    const body =
      [
        '/* TEAM */',
        ...leadersList,
        '',
        '/* CONTRIBUTORS */',
        ...contributorsList,
        '',
        '/* SITE */',
        'Standards: HTML5, CSS3, ECMAScript',
        'Software: Next.js, TypeScript, GraphQL, Apollo Client',
      ].join('\n') + '\n'

    return new NextResponse(body, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'public, max-age=86400, s-maxage=86400',
      },
    })
  } catch {
    return new NextResponse('humans.txt temporarily unavailable\n', {
      status: 500,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    })
  }
}



