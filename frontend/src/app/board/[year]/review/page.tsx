'use client'

import { useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
import { GetBoardCandidateClaimReviewsDocument } from 'types/__generated__/reviewQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const ClaimReviewsPage = () => {
  const router = useRouter()
  const { isSyncing, session } = useDjangoSession()
  const { year } = useParams<{ year: string }>()

  const {
    data: graphQLData,
    loading: isLoading,
    error: graphQLRequestError,
  } = useQuery(GetBoardCandidateClaimReviewsDocument, {
    skip: !year,
    variables: { login: session?.user?.login ?? '', year: Number.parseInt(year) },
  })

  const isCandidate = graphQLData?.boardOfDirectors?.candidate != null
  const isReviewer = graphQLData?.boardOfDirectors?.reviewer != null
  const claims = graphQLData?.boardCandidateClaims ?? []

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  if (isSyncing || isLoading) {
    return <LoadingSpinner />
  }

  if (!isReviewer || isCandidate) {
    return <AccessDeniedDisplay title="Access Denied" message="Cannot view this page." />
  }

  const handleClaimClick = (key: string, login: string | undefined) =>
    router.push(`/board/${year}/candidates/${login}/claims/${key}`)

  const sectionConfig = [
    {
      title: 'Claims to Review',
      items: claims.filter(
        (c) =>
          c.status === ClaimStatusEnum.Submitted &&
          !c.reviews.some((review) => review.reviewer.login === session?.user?.login)
      ),
    },
    {
      title: 'Reviewed Claims',
      items: claims.filter((c) =>
        c.reviews.some((review) => review.reviewer.login === session?.user?.login)
      ),
    },
  ]

  return (
    <div className="container mx-auto px-4 py-8 dark:bg-[#212529]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-600 dark:text-white">Claims</h1>
          <p className="text-gray-600 dark:text-gray-400">Candidate claims for {year} elections.</p>
        </div>
      </div>
      {sectionConfig.map(({ title, items }) => (
        <SecondaryCard key={title} title={title}>
          {items.length == 0 ? (
            <p> No {title.toLowerCase()}. </p>
          ) : (
            <div className="grid gap-2">
              {items.map((claim) => (
                <Button
                  disableAnimation
                  key={claim.key}
                  onPress={() => handleClaimClick(claim.key, claim.candidate.member?.login)}
                  className="h-24 flex-row justify-between bg-transparent dark:hover:bg-gray-900"
                >
                  <div className="flex min-w-0 flex-1 flex-col items-start justify-start p-1">
                    <h3 className="w-full min-w-0 truncate text-left text-xl leading-tight font-semibold dark:text-gray-300">
                      {claim.name}
                    </h3>
                    <p className="w-full min-w-0 truncate text-left leading-tight text-gray-600 dark:text-gray-300">
                      {claim.description}
                    </p>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="shrink-0 text-xs text-gray-600 dark:text-gray-400">
                        {formatDate(claim.createdAt)}
                      </span>
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          )}
        </SecondaryCard>
      ))}
    </div>
  )
}

export default ClaimReviewsPage
