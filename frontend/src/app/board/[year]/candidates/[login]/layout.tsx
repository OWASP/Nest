'use client'

import { useQuery } from '@apollo/client/react'
import { registerBreadcrumb } from 'contexts/BreadcrumbContext'
import { useParams } from 'next/navigation'
import { useEffect, type ReactNode } from 'react'
import { GetBoardCandidateNameDocument } from 'types/__generated__/boardQueries.generated'

export default function CandidateLayout({ children }: Readonly<{ children: ReactNode }>) {
  const { login, year } = useParams<{ login: string; year: string }>()
  const parsedYear = Number.parseInt(year)

  const { data } = useQuery(GetBoardCandidateNameDocument, {
    skip: !login || Number.isNaN(parsedYear),
    variables: { login, year: parsedYear },
  })

  const memberName = data?.boardCandidateProfile?.candidate.memberName

  useEffect(() => {
    if (!memberName) return
    const unregister = registerBreadcrumb({
      title: memberName,
      path: `/board/${year}/candidates/${login}`,
    })
    return unregister
  }, [memberName, login, year])

  return <>{children}</>
}
