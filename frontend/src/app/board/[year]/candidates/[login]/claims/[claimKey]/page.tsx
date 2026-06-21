'use client'

import { useQuery } from '@apollo/client/react'

import { Button } from '@heroui/button'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { toLower, upperFirst } from 'lodash'
import { useParams, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { FaPlus } from 'react-icons/fa6'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetClaimAndEvidencesDocument } from 'types/__generated__/claimQueries.generated'
import { ClaimStatusEnum } from 'types/__generated__/graphql'
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
    skip: !claimKey,
    variables: { key: claimKey, login, year: Number.parseInt(year) },
  })

  const claim = graphQLData?.boardCandidateClaim
  const evidences = graphQLData?.boardCandidateClaimEvidences ?? []

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError])

  if (isLoading || isSyncing) return <LoadingSpinner />

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

  if (session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
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
            {claim.status == ClaimStatusEnum.Draft && (
              <ActionButton onClick={handleAddEvidence}>
                <FaPlus className="mr-2" />
                {'Add Evidence'}
              </ActionButton>
            )}
            <ClaimActions claim={claim} login={login} year={year} />
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
                  key={evidence.key}
                  onPress={() => handleEvidenceClick(evidence.key)}
                  className="h-28 flex-col items-start justify-start bg-transparent p-4 dark:hover:bg-gray-900"
                >
                  <h3 className="w-full min-w-0 truncate text-left text-xl leading-tight font-semibold dark:text-gray-300">
                    {evidence.name}
                  </h3>
                  <p className="w-full min-w-0 truncate text-left leading-tight text-gray-600 dark:text-gray-300">
                    {evidence.description}
                  </p>
                  <span className="shrink-0 text-xs text-gray-600 dark:text-gray-400">
                    {formatDate(evidence.createdAt)}
                  </span>
                </Button>
              ))}
            </div>
          )}
        </SecondaryCard>
      </PageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default ClaimDetailsPage
