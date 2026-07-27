'use client'

import { useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Chip } from '@heroui/react'
import { useDjangoSession } from 'hooks/useDjangoSession'
import groupBy from 'lodash/groupBy'
import { useParams, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { ClaimStatusEnum, ReviewStatusEnum } from 'types/__generated__/graphql'
import { GetClaimsAndReviewsDocument } from 'types/__generated__/reviewQueries.generated'
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
  } = useQuery(GetClaimsAndReviewsDocument, {
    skip: !year || !session?.user?.login,
    variables: { sessionLogin: session?.user?.login ?? '', year: Number.parseInt(year) },
  })

  const isReviewer = graphQLData?.boardOfDirectors?.reviewer != null
  const isCandidate = graphQLData?.boardOfDirectors?.candidate != null
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
    return (
      <AccessDeniedDisplay
        title="Access Denied"
        message="You must be a reviewer to view this page."
      />
    )
  }

  const claimsToReview = claims.filter(
    (c) =>
      c.status === ClaimStatusEnum.Submitted &&
      !c.reviews.some((review) => review.reviewer.login === session?.user?.login)
  )
  const reviewedClaims = claims.filter((c) =>
    c.reviews.some((review) => review.reviewer.login === session?.user?.login)
  )

  const groupedClaimsToReview = groupBy(
    claimsToReview,
    (c) => c.candidate.member?.login ?? 'unknown'
  )
  const groupedReviewedClaims = groupBy(
    reviewedClaims,
    (c) => c.candidate.member?.login ?? 'unknown'
  )

  const groupedSections = [
    { title: 'Claims to Review', group: groupedClaimsToReview },
    { title: 'Reviewed Claims', group: groupedReviewedClaims },
  ]

  return (
    <div className="container mx-auto px-4 py-8 dark:bg-[#212529]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-600 dark:text-white">Claims</h1>
          <p className="text-gray-600 dark:text-gray-400">Candidate claims for {year} elections.</p>
        </div>
      </div>
      {groupedSections.map(({ title, group }) => (
        <SecondaryCard key={title} title={title}>
          {Object.keys(group).length === 0 ? (
            <p> No {title.toLowerCase()}. </p>
          ) : (
            <div className="space-y-6">
              {Object.entries(group).map(([login, candidateClaims]) => (
                <div key={login}>
                  <h4 className="mb-3 text-sm font-semibold text-gray-600 dark:text-gray-400">
                    @{login}
                    {candidateClaims[0].candidate.member?.name && (
                      <span className="font-normal">
                        {' '}
                        — {candidateClaims[0].candidate.member.name}
                      </span>
                    )}
                  </h4>
                  <div className="grid gap-2">
                    {candidateClaims.map((claim) => (
                      <Button
                        disableAnimation
                        key={claim.key}
                        onPress={() =>
                          router.push(`/board/${year}/candidates/${login}/claims/${claim.key}`)
                        }
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
                            {(() => {
                              const myReview = claim.reviews.find(
                                (r) => r.reviewer.login === session?.user?.login
                              )
                              if (!myReview) return null
                              return (
                                <Chip
                                  size="sm"
                                  variant="flat"
                                  color={
                                    myReview.status === ReviewStatusEnum.Approved
                                      ? 'success'
                                      : 'danger'
                                  }
                                  className="text-tiny h-5 shrink-0"
                                >
                                  {myReview.status === ReviewStatusEnum.Approved
                                    ? 'Approved'
                                    : 'Rejected'}
                                </Chip>
                              )
                            })()}
                          </div>
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </SecondaryCard>
      ))}
    </div>
  )
}

export default ClaimReviewsPage
