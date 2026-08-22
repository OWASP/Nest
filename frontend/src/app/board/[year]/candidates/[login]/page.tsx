'use client'

import { useQuery } from '@apollo/client/react'
import { registerBreadcrumb } from 'contexts/BreadcrumbContext'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetCandidateProfileDocument } from 'types/__generated__/boardQueries.generated'
import AnnotatedProfile from 'components/AnnotatedProfile'
import PageWrapper from 'components/cards/PageWrapper'
import LoadingSpinner from 'components/LoadingSpinner'

const CandidateProfilePage = () => {
  const { login, year } = useParams<{ login: string; year: string }>()
  const { isSyncing, session } = useDjangoSession()

  const parsedYear = Number.parseInt(year)

  const { data, error, loading } = useQuery(GetCandidateProfileDocument, {
    skip: isSyncing || Number.isNaN(parsedYear),
    variables: {
      login,
      sessionLogin: session?.user?.login ?? '',
      year: parsedYear,
    },
  })

  useEffect(() => {
    if (error) {
      handleAppError(error)
    }
  }, [error])

  const memberName = data?.boardCandidateProfile?.candidate.memberName
  useEffect(() => {
    if (!memberName) return
    const unregister = registerBreadcrumb({
      title: memberName,
      path: `/board/${year}/candidates/${login}`,
    })
    return unregister
  }, [memberName, login, year])

  if (isSyncing || loading) {
    return <LoadingSpinner />
  }

  if (Number.isNaN(parsedYear)) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Board Not Found"
        message={`Sorry, the board information for ${year} doesn't exist`}
      />
    )
  }

  if (error) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading profile"
        message="An error occurred while loading the candidate profile"
      />
    )
  }

  const claims = data?.boardCandidateClaims ?? []
  const isCandidate = data?.boardOfDirectors?.candidate != null && session?.user?.login === login
  const profile = data?.boardCandidateProfile

  if (!profile) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Profile Not Found"
        message="No profile exists for this candidate."
      />
    )
  }

  return (
    <PageWrapper>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-600 dark:text-white">
          {profile.candidate.memberName}
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">{year} Board Candidate</p>
      </div>
      <AnnotatedProfile
        claims={claims}
        isCandidate={isCandidate}
        login={login}
        rawMarkdown={profile.rawMarkdown}
        year={year}
      />
    </PageWrapper>
  )
}

export default CandidateProfilePage
