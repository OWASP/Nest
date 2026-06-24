'use client'

import { useLazyQuery, useQuery } from '@apollo/client/react'

import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { useParams } from 'next/navigation'
import { useEffect } from 'react'
import { FaDownload } from 'react-icons/fa6'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetBoardCandidateClaimDocument } from 'types/__generated__/claimQueries.generated'
import {
  GetBoardCandidateClaimEvidenceDocument,
  GetBoardCandidateClaimEvidenceFileUrlDocument,
} from 'types/__generated__/evidenceQueries.generated'
import { titleCaseWord } from 'utils/capitalize'
import { formatDate } from 'utils/dateFormatter'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ActionButton from 'components/ActionButton'
import Metadata from 'components/cards/Metadata'
import PageWrapper from 'components/cards/PageWrapper'
import EvidenceActions from 'components/EvidenceActions'
import LoadingSpinner from 'components/LoadingSpinner'

const EvidenceDetailsPage = () => {
  const { claimKey, evidenceKey, login, year } = useParams<{
    claimKey: string
    evidenceKey: string
    login: string
    year: string
  }>()
  const { isSyncing, session } = useDjangoSession()

  const {
    data: claimGraphQLData,
    error: claimGraphQLRequestError,
    loading: isClaimLoading,
  } = useQuery(GetBoardCandidateClaimDocument, {
    fetchPolicy: 'cache-and-network',
    skip: !claimKey,
    variables: { key: claimKey, login, year: Number.parseInt(year) },
  })

  const {
    data: evidenceGraphQLData,
    error: evidenceGraphQLRequestError,
    loading: isEvidenceLoading,
  } = useQuery(GetBoardCandidateClaimEvidenceDocument, {
    fetchPolicy: 'cache-and-network',
    skip: !evidenceKey,
    variables: { claimKey, key: evidenceKey, login, year: Number.parseInt(year) },
  })

  const [fetchFileUrl] = useLazyQuery(GetBoardCandidateClaimEvidenceFileUrlDocument)

  const claim = claimGraphQLData?.boardCandidateClaim
  const evidence = evidenceGraphQLData?.boardCandidateClaimEvidence

  useEffect(() => {
    if (claimGraphQLRequestError) {
      handleAppError(claimGraphQLRequestError)
    }
    if (evidenceGraphQLRequestError) {
      handleAppError(evidenceGraphQLRequestError)
    }
  }, [claimGraphQLRequestError, evidenceGraphQLRequestError])

  if (isClaimLoading || isEvidenceLoading || isSyncing) return <LoadingSpinner />

  if (claimGraphQLRequestError || evidenceGraphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading program"
        message="An error occurred while loading the evidence data"
      />
    )
  }

  if (!claimGraphQLData || !evidenceGraphQLData || !claim || !evidence) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Claim Not Found"
        message="Sorry, the evidence you're looking for doesn't exist."
      />
    )
  }

  if (session?.user?.login !== login) {
    return (
      <AccessDeniedDisplay title="Access Denied" message="You can only view your own claims." />
    )
  }

  const evidenceDetails = [
    { label: 'Name', value: titleCaseWord(evidence.name) },
    { label: 'Description', value: evidence.description },
    { label: 'Source URL', value: evidence.sourceUrl },
    { label: 'Last Updated', value: formatDate(evidence.updatedAt) },
  ]

  const handleDownloadEvidence = async () => {
    const { data } = await fetchFileUrl({
      variables: { claimKey, key: evidenceKey, login, year: Number.parseInt(year) },
    })
    const url = data?.boardCandidateClaimEvidenceFileUrl
    if (url) {
      const a = document.createElement('a')
      a.href = url
      a.target = '_blank'
      a.rel = 'noopener noreferrer'
      a.click()
    }
  }

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <PageWrapper>
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-600 dark:text-white">Evidence</h1>
          </div>
          <div className="flex items-center">
            {evidence.hasFile && (
              <ActionButton onClick={handleDownloadEvidence}>
                <FaDownload className="mr-2" />
                {'Download Evidence'}
              </ActionButton>
            )}
            <EvidenceActions evidence={evidence} claim={claim} login={login} year={year} />
          </div>
        </div>
        <Metadata details={evidenceDetails} detailsTitle="Evidence Details" />
      </PageWrapper>
    </BreadcrumbStyleProvider>
  )
}

export default EvidenceDetailsPage
