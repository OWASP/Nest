'use client'

import { useQuery } from '@apollo/client/react'
import { useParams } from 'next/navigation'
import React from 'react'

import { ErrorDisplay } from 'app/global-error'
import { GetCertificateDocument } from 'types/__generated__/certificateQueries.generated'
import { CertificateCard } from 'components/CertificateCard'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'

const CertificateVerificationPage: React.FC = () => {
  const { certificateId } = useParams<{ certificateId: string }>()

  const { data, loading, error } = useQuery(GetCertificateDocument, {
    variables: { id: certificateId },
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
  })

  if (loading && !data) {
    return <LoadingSpinner />
  }

  if (error && !data?.certificate) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Verification Error"
        message="An error occurred while verifying the certificate."
      />
    )
  }

  const certificate = data?.certificate

  if (!certificate) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Certificate Not Found"
        message="The certificate verification link is invalid or the certificate does not exist."
      />
    )
  }

  const displayName = certificate.githubUser.name || certificate.githubUser.login

  return (
    <PageLayout
      title={`Verify ${displayName}'s Certificate`}
      breadcrumbClassName="bg-[#f4f6fc] dark:bg-[#212529]"
    >
      <div className="container mx-auto flex w-full flex-1 flex-col items-center self-stretch px-4 py-4">
        <div className="relative flex w-full justify-center">
          <CertificateCard certificate={certificate} isPublicView={true} />
        </div>
      </div>
    </PageLayout>
  )
}

export default CertificateVerificationPage
