'use client'

import { useQuery } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useRef, useState } from 'react'
import { FaCopy, FaFilePdf, FaImage, FaLinkedin } from 'react-icons/fa6'

import { GetMyCertificateDocument } from 'types/__generated__/certificateQueries.generated'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import ActionButton from 'components/ActionButton'
import { CertificateCard, CERTIFICATE_LAYOUT } from 'components/CertificateCard'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'

const MyCertificatePage: React.FC = () => {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [isDownloading, setIsDownloading] = useState(false)
  const [isSavingPdf, setIsSavingPdf] = useState(false)
  const cardRef = useRef<HTMLDivElement>(null)

  const { data, loading, error } = useQuery(GetMyCertificateDocument, {
    skip: !session,
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
  })

  useEffect(() => {
    if (error) {
      addToast({
        title: 'Error',
        description: 'Failed to fetch your certificate.',
        color: 'danger',
      })
    }
  }, [error])

  if (status === 'loading') {
    return <LoadingSpinner />
  }

  if (!session) {
    return (
      <div className="container mx-auto flex min-h-[50vh] items-center justify-center px-4 py-16">
        <AccessDeniedDisplay
          title="Authentication Required"
          message="Please log in to view and manage your certificate."
        />
      </div>
    )
  }

  if (loading && !data) {
    return <LoadingSpinner />
  }

  const certificate = data?.myCertificate

  if (!certificate) {
    return (
      <PageLayout title="My Certificate">
        <div className="container mx-auto flex min-h-[50vh] max-w-lg flex-col items-center justify-center px-4 py-16 text-center">
          <h2 className="mb-2 text-2xl font-bold text-gray-600 dark:text-white">
            No Certificate Found
          </h2>
          <p className="mb-6 text-gray-600 dark:text-gray-400">
            You don&apos;t have a contributor certificate yet. Contribute to OWASP repositories to
            increase your contribution score and earn a certificate!
          </p>
          <ActionButton onClick={() => router.push('/contribute')}>Start Contributing</ActionButton>
        </div>
      </PageLayout>
    )
  }

  const getCertificateImageDataUrl = async (): Promise<string> => {
    const node = cardRef.current
    if (!node) throw new Error('Certificate element not found')
    const { toPng } = await import('html-to-image')
    return toPng(node, {
      cacheBust: true,
      style: { transform: 'scale(1)', transformOrigin: 'top center' },
      pixelRatio: 2,
    })
  }

  const handleSaveAsImage = async () => {
    setIsDownloading(true)
    try {
      const dataUrl = await getCertificateImageDataUrl()
      const link = document.createElement('a')
      link.download = `certificate-${certificate.id}.png`
      link.href = dataUrl
      link.click()
      addToast({ title: 'Downloaded', description: 'Certificate saved as PNG.', color: 'success' })
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to save certificate as image:', error)
      // Failed to save certificate
      addToast({
        title: 'Error',
        description: 'Failed to save certificate as image.',
        color: 'danger',
      })
    } finally {
      setIsDownloading(false)
    }
  }

  const handleSaveAsPdf = async () => {
    setIsSavingPdf(true)
    try {
      const dataUrl = await getCertificateImageDataUrl()
      const { jsPDF } = await import('jspdf')

      const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'px',
        format: [CERTIFICATE_LAYOUT.width, CERTIFICATE_LAYOUT.height],
      })
      pdf.addImage(dataUrl, 'PNG', 0, 0, CERTIFICATE_LAYOUT.width, CERTIFICATE_LAYOUT.height)

      const verifyUrl = `${globalThis.location.origin}/certificate/${certificate.id}`
      pdf.link(
        CERTIFICATE_LAYOUT.verifyLink.x,
        CERTIFICATE_LAYOUT.verifyLink.y,
        CERTIFICATE_LAYOUT.verifyLink.width,
        CERTIFICATE_LAYOUT.verifyLink.height,
        { url: verifyUrl }
      )

      pdf.save(`certificate-${certificate.id}-${new Date().toISOString().split('T')[0]}.pdf`)
      addToast({ title: 'Downloaded', description: 'Certificate saved as PDF.', color: 'success' })
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to save certificate as PDF:', error)
      addToast({
        title: 'Error',
        description: 'Failed to save certificate as PDF.',
        color: 'danger',
      })
    } finally {
      setIsSavingPdf(false)
    }
  }

  const handleCopyLink = () => {
    const shareUrl = `${globalThis.location.origin}/certificate/${certificate.id}`
    navigator.clipboard
      .writeText(shareUrl)
      .then(() => {
        addToast({
          title: 'Link Copied',
          description: 'Shareable verification link copied to clipboard!',
          color: 'success',
        })
      })
      .catch(() => {
        addToast({
          title: 'Copy Failed',
          description: 'Could not copy link to clipboard.',
          color: 'danger',
        })
      })
  }

  const handleShareLinkedIn = () => {
    const certUrl = `${globalThis.location.origin}/certificate/${certificate.id}`
    const issuedDate = new Date(certificate.issuedAt)
    const params = new URLSearchParams({
      startTask: 'CERTIFICATION_NAME',
      name: 'OWASP Foundation Contributor Certificate',
      organizationId: '250673',
      issueYear: String(issuedDate.getFullYear()),
      issueMonth: String(issuedDate.getMonth() + 1),
      certUrl,
      certId: certificate.id,
    })
    window.open(
      `https://www.linkedin.com/profile/add?${params.toString()}`,
      '_blank',
      'noopener,noreferrer'
    )
  }

  const displayName = certificate.githubUser.name || certificate.githubUser.login

  return (
    <PageLayout title={`${displayName}'s Certificate`}>
      <div className="container mx-auto flex flex-col items-center px-4 py-8">
        <div className="flex w-full justify-center">
          <CertificateCard certificate={certificate} isPublicView={false} cardRef={cardRef} />
        </div>

        <div className="mt-6 w-full max-w-3xl rounded-2xl border border-gray-200 bg-white p-4 shadow-sm sm:p-5 dark:border-gray-800 dark:bg-[#1E2227]">
          <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-center sm:gap-4">
            <Button
              onPress={handleSaveAsImage}
              isDisabled={isDownloading}
              size="lg"
              variant="bordered"
              className="w-full border-[#1D70B8] font-semibold text-[#1D70B8] hover:bg-[#1D70B8] hover:text-white sm:w-auto dark:hover:text-white"
            >
              <FaImage size={18} />
              {isDownloading ? 'Downloading...' : 'Save as Image'}
            </Button>

            <Button
              onPress={handleSaveAsPdf}
              isDisabled={isSavingPdf}
              size="lg"
              variant="bordered"
              className="w-full border-[#1D70B8] font-semibold text-[#1D70B8] hover:bg-[#1D70B8] hover:text-white sm:w-auto dark:hover:text-white"
            >
              <FaFilePdf size={18} />
              {isSavingPdf ? 'Preparing...' : 'Save as PDF'}
            </Button>

            <Button
              onPress={handleCopyLink}
              size="lg"
              variant="bordered"
              className="w-full border-[#1D70B8] font-semibold text-[#1D70B8] hover:bg-[#1D70B8] hover:text-white sm:w-auto dark:hover:text-white"
            >
              <FaCopy size={18} />
              Copy Shareable Link
            </Button>

            <Button
              onPress={handleShareLinkedIn}
              size="lg"
              variant="solid"
              className="w-full bg-[#1D70B8] font-semibold text-white hover:bg-[#155a96] sm:w-auto"
            >
              <FaLinkedin size={18} />
              Add to LinkedIn
            </Button>
          </div>
        </div>
      </div>
    </PageLayout>
  )
}

export default MyCertificatePage
