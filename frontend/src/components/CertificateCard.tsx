'use client'

import Image from 'next/image'
import React, { useRef, useEffect, useState } from 'react'
import {
  FaAward,
  FaCalendarDays,
  FaChartBar,
  FaCircleCheck,
  FaCircleXmark,
  FaGithub,
  FaGlobe,
  FaShieldHalved,
} from 'react-icons/fa6'
import type { Certificate } from 'types/certificate'
import { formatDate } from 'utils/dateFormatter'

const BorderFrame: React.FC = () => (
  <div className="pointer-events-none absolute inset-0 z-10">
    <div className="absolute inset-[12px] border-[8px] border-[#0B2545]" />
    <div className="absolute inset-[22px] border-[2.5px] border-[#1D70B8]" />
    <div className="absolute top-[34px] left-[34px] h-[50px] w-[50px] border-t-[4px] border-l-[4px] border-[#1D70B8] opacity-[0.85]" />
    <div className="absolute top-[42px] left-[42px] h-[34px] w-[34px] border-t-[2px] border-l-[2px] border-[#1D70B8] opacity-[0.45]" />
    <div className="absolute right-[34px] bottom-[34px] h-[50px] w-[50px] border-r-[4px] border-b-[4px] border-[#1D70B8] opacity-[0.85]" />
    <div className="absolute right-[42px] bottom-[42px] h-[34px] w-[34px] border-r-[2px] border-b-[2px] border-[#1D70B8] opacity-[0.45]" />
  </div>
)

const Header: React.FC = () => (
  <div className="flex flex-col items-center pt-2 text-center">
    <div className="relative mb-2.5 h-[52px] w-[192px]">
      <Image src="/img/OWASP_logo.svg" alt="OWASP Logo" fill priority className="object-contain" />
    </div>
    <span className="mb-3 block text-[11px] font-semibold tracking-[0.22em] text-[#8fa3b8] uppercase">
      Open Worldwide Application Security Project
    </span>
    <h1 className="mb-3 text-[32px] leading-none font-extrabold tracking-[0.12em] text-[#0B2545] uppercase">
      Certificate of Recognition
    </h1>
    <div className="mt-0 flex w-[200px] items-center">
      <div className="h-[1.5px] flex-1 bg-[#1D70B8]" />
      <div className="mx-2 h-2.5 w-2.5 shrink-0 rotate-45 bg-[#1D70B8]" />
      <div className="h-[1.5px] flex-1 bg-[#1D70B8]" />
    </div>
  </div>
)

interface RecipientProps {
  name?: string | null
  login: string
  avatarUrl: string
}

const Recipient: React.FC<RecipientProps> = ({ name, login, avatarUrl }) => {
  const displayName = name || login
  return (
    <div className="mt-3 mb-0 flex w-full flex-col items-center">
      <span className="mb-4 block text-center text-[13px] font-bold tracking-[0.22em] text-[#6B7280] uppercase">
        Proudly Presented To
      </span>
      <div className="flex flex-row items-center justify-center gap-5">
        <div className="relative h-24 w-24 shrink-0 overflow-hidden rounded-full border border-[#0B2545]/20 shadow-[0_2px_12px_rgba(11,37,69,0.08)]">
          <Image src={avatarUrl} alt={displayName} fill sizes="96px" className="object-cover" />
        </div>
        <div className="flex h-24 flex-col justify-center text-left">
          <span className="block font-sans text-[32px] leading-none font-bold text-[#0B2545]">
            {displayName}
          </span>
          <div className="mt-2.5 flex flex-row items-center gap-2">
            <FaGithub className="shrink-0 text-[18px] text-[#111827]" />
            <span className="text-[15px] leading-none font-semibold text-[#1D70B8]">@{login}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

const RecognitionText: React.FC = () => (
  <p className="mx-auto mt-2 max-w-[560px] text-center text-[16px] leading-[1.8] font-medium text-slate-700 italic">
    &quot;In recognition of exceptional contributions to the global OWASP open-source ecosystem and
    commitment to collaborative innovation.&quot;
  </p>
)

interface LabelProps {
  children: React.ReactNode
  size?: 'sm' | 'md'
}

const Label: React.FC<LabelProps> = ({ children, size = 'md' }) => (
  <span
    className={`${
      size === 'sm' ? 'text-[11px]' : 'text-[13px]'
    } font-semibold tracking-[0.08em] text-[#1D70B8] uppercase`}
  >
    {children}
  </span>
)

interface MetricsProps {
  score: number
  tier: string
}

const Metrics: React.FC<MetricsProps> = ({ score, tier }) => (
  <div className="mx-auto mt-2 flex h-[88px] w-full flex-row items-center justify-between rounded-[16px] border border-[#d9d9df] bg-white px-4 py-2 font-sans shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
    <div className="flex flex-1 flex-row items-center justify-center gap-2">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#1D70B8]">
        <FaChartBar size={22} className="text-white" />
      </div>
      <div className="flex flex-col items-center justify-center text-center leading-none">
        <Label size="sm">Contribution Score</Label>
        <span className="mt-1.5 text-[28px] leading-[0.95] font-extrabold text-[#111827]">
          {score}
        </span>
        <span className="mt-0.5 text-[12px] font-bold tracking-[0.15em] text-[#4B5563] uppercase">
          Points
        </span>
      </div>
    </div>
    <div className="h-[56px] w-[1px] shrink-0 bg-[#dcdce3]" />
    <div className="flex flex-1 flex-row items-center justify-center gap-2">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#1D70B8]">
        <FaAward size={22} className="text-white" />
      </div>
      <div className="flex flex-col items-center justify-center text-center leading-none">
        <Label size="sm">Achievement Tier</Label>
        <span className="mt-1.5 text-[20px] leading-[0.95] font-extrabold tracking-[0.12em] text-[#111827]">
          {tier.toUpperCase()}
        </span>
      </div>
    </div>
  </div>
)

interface FooterProps {
  id: string
  issuedAt: string
}

const Footer: React.FC<FooterProps> = ({ id, issuedAt }) => (
  <div className="mx-auto mt-6 flex w-full max-w-[820px] flex-row items-center justify-between font-sans">
    <div className="flex flex-1 flex-row items-center justify-center gap-4">
      <FaShieldHalved className="shrink-0 text-[28px] text-[#1D70B8]" />
      <div className="flex flex-col items-start justify-center leading-none">
        <Label>Certificate ID</Label>
        <span
          className="mt-1.5 block font-mono text-[14px] font-bold text-[#111827] uppercase"
          title={id}
        >
          {id}
        </span>
      </div>
    </div>
    <div className="h-10 w-[1px] shrink-0 bg-gray-200" />
    <div className="flex flex-1 flex-row items-center justify-center gap-4">
      <FaCalendarDays className="shrink-0 text-[28px] text-[#1D70B8]" />
      <div className="flex flex-col items-start justify-center leading-none">
        <Label>Issued On</Label>
        <span className="mt-1.5 block text-[14px] font-bold text-[#111827]">
          {formatDate(issuedAt)}
        </span>
      </div>
    </div>
    <div className="h-10 w-[1px] shrink-0 bg-gray-200" />
    <div className="flex flex-1 flex-row items-center justify-center gap-4">
      <FaGlobe className="shrink-0 text-[28px] text-[#1D70B8]" />
      <div className="flex max-w-[220px] flex-col items-start justify-center leading-none">
        <Label>Verify Certificate</Label>
        <a
          href={`/certificate/${id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-1.5 block max-w-[200px] truncate text-[14px] font-bold text-[#111827] hover:underline"
        >
          nest.owasp.org
        </a>
      </div>
    </div>
  </div>
)

const VerificationBadge: React.FC = () => (
  <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 rounded-full border border-green-200 bg-green-50 px-3 py-1.5 text-green-700 shadow-sm">
    <FaCircleCheck className="shrink-0 text-sm text-green-500" />
    <span className="font-sans text-[10px] font-bold tracking-wider uppercase">
      Verified Contributor
    </span>
  </div>
)

const RevokedBadge: React.FC = () => (
  <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 rounded-full border border-red-200 bg-red-50 px-3 py-1.5 text-red-700 shadow-sm">
    <FaCircleXmark className="shrink-0 text-sm text-red-500" />
    <span className="font-sans text-[10px] font-bold tracking-wider uppercase">Revoked</span>
  </div>
)

const RevokedWatermark: React.FC = () => (
  <div className="pointer-events-none absolute inset-0 z-30 flex items-center justify-center overflow-hidden bg-white/20 backdrop-blur-[0.5px] select-none">
    <div className="rotate-[-25deg] rounded-3xl border-[10px] border-red-600/10 px-10 py-3 text-[90px] font-black tracking-[0.15em] text-red-600/10 uppercase shadow-[inset_0_0_0_4px_rgba(220,38,38,0.05)]">
      Revoked
    </div>
  </div>
)

export const CERTIFICATE_LAYOUT = {
  width: 842,
  height: 595,
  verifyLink: {
    x: 560,
    y: 530,
    width: 260,
    height: 40,
  },
}

interface CertificateCardProps {
  certificate: Certificate
  isPublicView?: boolean
  cardRef?: React.RefObject<HTMLDivElement | null>
}

export const CertificateCard: React.FC<CertificateCardProps> = ({
  certificate,
  isPublicView = false,
  cardRef,
}) => {
  const { id, tier, issuedAt, score, isVerified, githubUser } = certificate
  const [scale, setScale] = useState(1)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const parentWidth = containerRef.current.clientWidth || window.innerWidth
        const newScale = Math.min(1, (parentWidth - 32) / CERTIFICATE_LAYOUT.width)
        setScale(newScale)
      }
    }
    handleResize()

    let resizeObserver: ResizeObserver | null = null
    if (typeof window !== 'undefined' && 'ResizeObserver' in window && containerRef.current) {
      resizeObserver = new ResizeObserver(() => {
        handleResize()
      })
      resizeObserver.observe(containerRef.current)
    }

    window.addEventListener('resize', handleResize)
    return () => {
      if (resizeObserver) {
        resizeObserver.disconnect()
      }
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  const scaledHeight = Math.round(CERTIFICATE_LAYOUT.height * scale)

  return (
    <div ref={containerRef} className="flex w-full justify-center py-8">
      {/* Wrapper sized to scaled dimensions — shadow here avoids filter artifacts on the scaled element */}
      <div
        className="relative overflow-hidden shadow-[0_8px_40px_rgba(11,37,69,0.18),0_2px_8px_rgba(0,0,0,0.08)]"
        style={{
          width: `${Math.round(CERTIFICATE_LAYOUT.width * scale)}px`,
          height: `${scaledHeight}px`,
        }}
      >
        <div
          ref={cardRef}
          id="certificate-card"
          className="absolute top-0 left-0 origin-top-left"
          style={{
            width: `${CERTIFICATE_LAYOUT.width}px`,
            height: `${CERTIFICATE_LAYOUT.height}px`,
            transform: `scale(${scale})`,
          }}
        >
          <div className="relative h-full w-full overflow-hidden bg-white p-2.5">
            <BorderFrame />
            <div className="relative flex h-full w-full flex-col overflow-hidden rounded-[2px] border-2 border-gray-200 bg-white">
              {isPublicView && (isVerified ? <VerificationBadge /> : <RevokedBadge />)}
              {!isVerified && <RevokedWatermark />}
              <div className="flex flex-1 flex-col justify-between px-12 pt-6 pb-10">
                <Header />
                <Recipient
                  name={githubUser.name}
                  login={githubUser.login}
                  avatarUrl={githubUser.avatarUrl}
                />
                <RecognitionText />
                <Metrics score={score} tier={tier} />
                <Footer id={id} issuedAt={issuedAt} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
