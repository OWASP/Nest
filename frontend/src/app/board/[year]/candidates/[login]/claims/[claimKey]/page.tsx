'use client'

import { useQuery } from '@apollo/client/react'

import { Button } from '@heroui/button'
import { Chip } from '@heroui/react'
import { BreadcrumbStyleProvider, registerBreadcrumb } from 'contexts/BreadcrumbContext'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { toLower, upperFirst } from 'lodash'
import { useParams, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { FaPlus } from 'react-icons/fa6'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetClaimAndEvidencesDocument } from 'types/__generated__/claimQueries.generated'
import { ClaimStatusEnum, ReviewStatusEnum } from 'types/__generated__/graphql'
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ActionButton from 'components/ActionButton'
import Metadata from 'components/cards/Metadata'
import PageWrapper from 'components/cards/PageWrapper'
import ClaimActions from 'components/ClaimActions'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const ClaimDetailsPage = () => {
  const router = useRouter()
  const { claimKey, login, year } = useParams<{ claimKey: string; login: string; year: string }>()
  const { isSyncing, session } = useDjangoSession()
  const {
    data: graphQLData,
    loading: isLoading,
    error: graphQLRequestError,
  } = useQuery(GetClaimAndEvidencesDocument, {
    fetchPolicy: 'cache-and-network',
    skip: !claimKey || !year || !session?.user?.login,
    variables: {
      key: claimKey,
      login,
      sessionLogin: session?.user?.login ?? '',
      year: Number.parseInt(year),
    },
  })

  const isReviewer = graphQLData?.boardOfDirectors?.reviewer != null
  const claim = graphQLData?.boardCandidateClaim
  const evidences = graphQLData?.boardCandidateClaimEvidences ?? []
  const hasReviewed =
    claim?.reviews?.some((r) => r.reviewer?.login === session?.user?.login) ?? false

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  useEffect(() => {
    if (!claim) return
    const unregister = registerBreadcrumb({
      title: claim.name,
      path: `/board/${year}/candidates/${login}/claims/${claimKey}`,
    })
    return unregister
  }, [claim, claimKey, login, year])

  if (isLoading || isSyncing) return <LoadingSpinner />

  if (session?.user?.login !== login && !isReviewer) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
    )
  }

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading claim"
        message="An error occurred while loading the claim data"
      />
    )
  }

  if (!graphQLData || !claim) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Claim Not Found"
        message="Sorry, the claim you're looking for doesn't exist."
      />
    )
  }

  const claimDetails = [
    { label: 'Name', value: titleCaseWord(claim.name) },
    { label: 'Description', value: claim.description },
    { label: 'Status', value: upperFirst(toLower(claim.status)) },
    { label: 'Last Updated', value: formatDate(claim.updatedAt) },
  ]

  const handleAddEvidence = () =>
    router.push(`/board/${year}/candidates/${login}/claims/${claimKey}/evidences/create`)

  const handleEvidenceClick = (evidenceKey: string) =>
    router.push(`/board/${year}/candidates/${login}/claims/${claimKey}/evidences/${evidenceKey}`)

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <PageWrapper>
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-600 dark:text-white">Claim</h1>
          </div>
          <div className="flex items-center">
            {claim.status == ClaimStatusEnum.Draft && session?.user?.login == login && (
              <ActionButton onClick={handleAddEvidence}>
                <FaPlus className="mr-2" />
                {'Add Evidence'}
              </ActionButton>
            )}
            <ClaimActions
              claim={claim}
              hasReviewed={hasReviewed}
              isReviewer={isReviewer}
              login={login}
              year={year}
            />
          </div>
        </div>
        <Metadata details={claimDetails} detailsTitle="Claim Details" />
        <SecondaryCard title="Evidences">
          {evidences.length == 0 ? (
            <p> No evidences. </p>
          ) : (
            <div className="grid gap-4">
              {evidences.map((evidence) => (
                <Button
                  disableAnimation
                  key={evidence.key}
                  onPress={() => handleEvidenceClick(evidence.key)}
                  className="h-24 w-full flex-row justify-between bg-transparent dark:hover:bg-gray-900"
                >
                  <div className="flex min-w-0 flex-1 flex-col items-start justify-start p-1">
                    <h3 className="w-full min-w-0 truncate text-left text-xl leading-tight font-semibold dark:text-gray-300">
                      {evidence.name}
                    </h3>
                    <p className="w-full min-w-0 truncate text-left leading-tight text-gray-600 dark:text-gray-300">
                      {evidence.description}
                    </p>
                    <div className="mt-1 flex items-center gap-2">
                      <span className="shrink-0 text-xs text-gray-600 dark:text-gray-400">
                        {formatDate(evidence.createdAt)}
                      </span>
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          )}
        </SecondaryCard>
        <SecondaryCard title="Reviews">
          {claim.reviews.length === 0 ? (
            <p> No reviews. </p>
          ) : (
            <div className="grid gap-4">
              {claim.reviews.map((review) => (
                <div
                  key={review.id}
                  className="h-28 flex-col items-start justify-start rounded-xl border border-gray-200 bg-transparent p-4 dark:border-gray-800"
                >
                  <div className="flex items-center gap-2">
                    <h3 className="min-w-0 truncate text-left text-xl leading-tight font-semibold dark:text-gray-300">
                      {review.reviewer?.login ?? 'Unknown Reviewer'}
                    </h3>
                  </div>
                  <p className="mt-2 flex-1 truncate text-left leading-tight text-gray-600 dark:text-gray-300">
                    {review.notes || 'No notes provided.'}
                  </p>
                  <span className="mt-2 flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                    {formatDate(review.createdAt)}
                    <Chip
                      size="sm"
                      variant="flat"
                      color={review.status === ReviewStatusEnum.Approved ? 'success' : 'danger'}
                      className="text-tiny h-5 shrink-0"
                    >
                      {upperFirst(toLower(review.status))}
                    </Chip>
                  </span>
                </div>
              ))}
            </div>
          )}
        </SecondaryCard>
      </PageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ClaimDetailsPage
