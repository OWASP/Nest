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
    <PageLayout title={`Verify ${displayName}'s Certificate`}>
      <div className="container mx-auto flex flex-col items-center px-4 py-8">
        {/* Verification Status Header */}
        {certificate.isVerified ? (
          <div className="mb-6 flex w-full max-w-[842px] flex-col items-center justify-between gap-4 rounded-xl border border-green-200/30 bg-green-50/5 px-5 py-4 sm:flex-row dark:border-green-900/20 dark:bg-green-950/5">
            <div className="flex flex-col items-center gap-3.5 text-center sm:flex-row sm:items-start sm:text-left">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-green-100/80 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                <FaCircleCheck size={22} />
              </div>
              <div className="flex flex-col justify-center">
                <h2 className="text-base font-extrabold tracking-tight text-gray-900 dark:text-white">
                  Verified Certificate
                </h2>
                <p className="mt-1 text-xs leading-relaxed text-gray-500 dark:text-gray-400">
                  This is an official verification record from the OWASP Nest registry, confirming
                  active contributions and achievements.
                </p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-1.5 rounded-full border border-green-200 bg-green-50 px-3 py-1 text-[10px] font-black tracking-widest text-green-700 uppercase dark:border-green-900/30 dark:bg-green-950/20 dark:text-green-400">
              Valid
            </div>
          </div>
        ) : (
          <div className="mb-6 flex w-full max-w-[842px] flex-col items-center justify-between gap-4 rounded-xl border border-red-200/30 bg-red-50/5 px-5 py-4 sm:flex-row dark:border-red-900/20 dark:bg-red-950/5">
            <div className="flex flex-col items-center gap-3.5 text-center sm:flex-row sm:items-start sm:text-left">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-red-100/80 text-red-700 dark:bg-red-900/30 dark:text-red-400">
                <FaCircleXmark size={22} />
              </div>
              <div className="flex flex-col justify-center">
                <h2 className="text-base font-extrabold tracking-tight text-gray-900 dark:text-white">
                  Revoked Certificate
                </h2>
                <p className="mt-1 text-xs leading-relaxed text-gray-500 dark:text-gray-400">
                  This certificate has been revoked and is no longer recognized as a valid record by
                  the OWASP Registry.
                </p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-1.5 rounded-full border border-red-200 bg-red-50 px-3 py-1 text-[10px] font-black tracking-widest text-red-700 uppercase dark:border-red-900/30 dark:bg-red-950/20 dark:text-red-400">
              Revoked
            </div>
          </div>
        )}

        {/* Certificate Rendering */}
        <div className="flex w-full justify-center">
          <CertificateCard certificate={certificate} isPublicView={true} />
        </div>
      </div>
    </PageLayout>
  )
}

export default CertificateVerificationPage
