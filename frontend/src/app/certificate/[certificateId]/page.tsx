'use client'

import { useQuery } from '@apollo/client/react'
import { useParams } from 'next/navigation'
import React from 'react'
import { FaCircleCheck, FaCircleXmark } from 'react-icons/fa6'

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
          {certificate.isVerified ? (
            <div className="absolute -bottom-3 left-1/2 z-20 -translate-x-1/2 md:bottom-0">
              <div className="flex items-center gap-3 rounded-full border border-green-300 bg-white/95 px-5 py-2.5 shadow-lg backdrop-blur-sm dark:border-green-600/50 dark:bg-gray-900/95">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-green-500 text-white">
                  <FaCircleCheck size={14} />
                </div>
                <span className="text-[14px] font-bold whitespace-nowrap text-gray-800 dark:text-white">
                  Verified Certificate
                </span>
                <span className="rounded-full bg-green-500 px-3 py-0.5 text-[11px] font-black tracking-widest text-white uppercase">
                  Valid
                </span>
              </div>
            </div>
          ) : (
            <div className="absolute bottom-0 left-1/2 z-20 -translate-x-1/2">
              <div className="flex items-center gap-3 rounded-full border border-red-300 bg-white/95 px-5 py-2.5 shadow-lg backdrop-blur-sm dark:border-red-600/50 dark:bg-gray-900/95">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-red-500 text-white">
                  <FaCircleXmark size={14} />
                </div>
                <span className="text-[14px] font-bold whitespace-nowrap text-gray-800 dark:text-white">
                  Revoked Certificate
                </span>
                <span className="rounded-full bg-red-500 px-3 py-0.5 text-[11px] font-black tracking-widest text-white uppercase">
                  Revoked
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  )
}

export default CertificateVerificationPage
