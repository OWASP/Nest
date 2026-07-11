'use client'

import { useQuery } from '@apollo/client/react'
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
      <PageLayout title="My Certificate" breadcrumbClassName="bg-[#f4f6fc] dark:bg-[#212529]">
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

  const getCertificateImageDataUrl = async (pixelRatio = 2): Promise<string> => {
    const node = cardRef.current
    if (!node) throw new Error('Certificate element not found')
    const { toPng } = await import('html-to-image')
    return toPng(node, {
      cacheBust: true,
      style: { transform: 'scale(1)', transformOrigin: 'top center' },
      pixelRatio,
    })
  }

  const handleSaveAsImage = async () => {
    if (isDownloading) return
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
    if (isSavingPdf) return
    setIsSavingPdf(true)
    try {
      const PDF_PIXEL_RATIO = 4
      const dataUrl = await getCertificateImageDataUrl(PDF_PIXEL_RATIO)
      const { jsPDF } = await import('jspdf')

      const CSS_PX_PER_INCH = 96
      const PT_PER_INCH = 72
      const widthPt = (CERTIFICATE_LAYOUT.width / CSS_PX_PER_INCH) * PT_PER_INCH
      const heightPt = (CERTIFICATE_LAYOUT.height / CSS_PX_PER_INCH) * PT_PER_INCH

      const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'pt',
        format: [widthPt, heightPt],
      })
      pdf.addImage(dataUrl, 'PNG', 0, 0, widthPt, heightPt)

      const pxToPt = (px: number) => (px / 96) * 72
      const verifyUrl = certificateUrl
      pdf.link(
        pxToPt(CERTIFICATE_LAYOUT.verifyLink.x),
        pxToPt(CERTIFICATE_LAYOUT.verifyLink.y),
        pxToPt(CERTIFICATE_LAYOUT.verifyLink.width),
        pxToPt(CERTIFICATE_LAYOUT.verifyLink.height),
        { url: verifyUrl }
      )

      const linkEl = cardRef.current?.querySelector('[data-github-link="true"]')
      if (linkEl && cardRef.current) {
        let x = 0
        let y = 0
        let el: HTMLElement | null = linkEl as HTMLElement
        while (el && el !== cardRef.current) {
          x += el.offsetLeft
          y += el.offsetTop
          el = el.offsetParent as HTMLElement | null
        }
        pdf.link(
          pxToPt(x),
          pxToPt(y),
          pxToPt((linkEl as HTMLElement).offsetWidth),
          pxToPt((linkEl as HTMLElement).offsetHeight),
          { url: `https://github.com/${certificate.githubUser.login}` }
        )
      }

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
    const shareUrl = certificateUrl
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
    const certUrl = certificateUrl
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

  const certificateUrl = `${globalThis.location?.origin ?? ''}/certificate/${certificate.id}`
  const displayName = certificate.githubUser.name || certificate.githubUser.login

  return (
    <PageLayout
      title={`${displayName}'s Certificate`}
      breadcrumbClassName="bg-[#f4f6fc] dark:bg-[#212529]"
    >
      <div className="container mx-auto mb-auto flex flex-col items-center justify-center gap-4 px-4 pt-2 pb-3 md:flex-row md:items-start md:gap-8 lg:gap-10">
        <div className="flex w-full max-w-[842px] min-w-0 flex-1 justify-center md:justify-end">
          <CertificateCard certificate={certificate} isPublicView={false} cardRef={cardRef} />
        </div>

        <div className="w-full max-w-md shrink-0 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm md:w-64 md:max-w-none md:self-center lg:w-80 lg:p-5 dark:border-gray-700 dark:bg-gray-800">
          <div className="grid grid-cols-2 gap-2.5 sm:gap-3.5 md:grid-cols-1">
            <ActionButton
              onClick={handleSaveAsImage}
              isDisabled={isDownloading}
              className="w-full whitespace-normal"
            >
              <FaImage size={18} />
              {isDownloading ? 'Downloading...' : 'Save as Image'}
            </ActionButton>

            <ActionButton
              onClick={handleSaveAsPdf}
              isDisabled={isSavingPdf}
              className="w-full whitespace-normal"
            >
              <FaFilePdf size={18} />
              {isSavingPdf ? 'Preparing...' : 'Save as PDF'}
            </ActionButton>

            <ActionButton onClick={handleCopyLink} className="w-full whitespace-normal">
              <FaCopy size={18} />
              Copy Link
            </ActionButton>

            <ActionButton
              onClick={handleShareLinkedIn}
              className="w-full border-transparent bg-[#1D7BD7] whitespace-normal text-white hover:bg-[#155a96] hover:text-white dark:hover:text-white"
            >
              <FaLinkedin size={18} />
              Add to LinkedIn
            </ActionButton>
          </div>
        </div>
      </div>
    </PageLayout>
  )
}

export default MyCertificatePage
