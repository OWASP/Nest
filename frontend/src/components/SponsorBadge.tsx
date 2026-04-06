import Image from 'next/image'
import Link from 'next/link'
import type React from 'react'
import { FaExternalLinkAlt, FaStar } from 'react-icons/fa'

export interface SponsorInfo {
  key: string
  name: string
  sponsorType: string
  imageUrl: string
  url: string
  description?: string
}

const TIER_CONFIG: Record<
  string,
  {
    label: string
    ring: string
    badge: string
    logoBg: string
    logoText: string
    glow: string
    icon: string
  }
> = {
  diamond: {
    label: 'Diamond Sponsor',
    ring: 'ring-1 ring-cyan-400/40 dark:ring-cyan-400/25',
    badge: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-400/10 dark:text-cyan-300',
    logoBg: 'bg-white dark:bg-white',
    logoText: 'text-cyan-800 dark:text-cyan-800',
    glow: 'shadow-[0_0_0_1px_rgba(34,211,238,0.1)] dark:shadow-[0_0_24px_rgba(34,211,238,0.07)]',
    icon: '💎',
  },
  platinum: {
    label: 'Platinum Sponsor',
    ring: 'ring-1 ring-slate-300/40 dark:ring-slate-400/30',
    badge: 'bg-slate-100 text-slate-700 dark:bg-slate-700/50 dark:text-slate-200',
    logoBg: 'bg-white dark:bg-white',
    logoText: 'text-slate-700 dark:text-slate-700',
    glow: 'shadow-[0_0_0_1px_rgba(148,163,184,0.15)] dark:shadow-[0_0_24px_rgba(148,163,184,0.06)]',
    icon: '✦',
  },
  gold: {
    label: 'Gold Sponsor',
    ring: 'ring-1 ring-amber-400/40 dark:ring-amber-400/25',
    badge: 'bg-amber-100 text-amber-800 dark:bg-amber-400/10 dark:text-amber-300',
    logoBg: 'bg-white dark:bg-white',
    logoText: 'text-amber-800 dark:text-amber-800',
    glow: 'shadow-[0_0_0_1px_rgba(251,191,36,0.1)] dark:shadow-[0_0_24px_rgba(251,191,36,0.07)]',
    icon: '★',
  },
  silver: {
    label: 'Silver Sponsor',
    ring: 'ring-1 ring-gray-300/40 dark:ring-gray-500/30',
    badge: 'bg-gray-100 text-gray-700 dark:bg-gray-700/40 dark:text-gray-300',
    logoBg: 'bg-white dark:bg-white',
    logoText: 'text-gray-700 dark:text-gray-700',
    glow: '',
    icon: '◆',
  },
  default: {
    label: 'Sponsor',
    ring: 'ring-1 ring-gray-200/40 dark:ring-gray-700/40',
    badge: 'bg-gray-100 text-gray-600 dark:bg-gray-800/60 dark:text-gray-400',
    logoBg: 'bg-white dark:bg-white',
    logoText: 'text-gray-700 dark:text-gray-700',
    glow: '',
    icon: '◇',
  },
}

const getTier = (sponsorType: string) =>
  TIER_CONFIG[sponsorType?.toLowerCase()] ?? TIER_CONFIG.default

interface SponsorBadgeProps {
  sponsor: SponsorInfo
  variant?: 'compact' | 'card'
}

const SponsorBadge: React.FC<SponsorBadgeProps> = ({ sponsor, variant = 'compact' }) => {
  const tier = getTier(sponsor.sponsorType)

  if (variant === 'card') {
    return (
      <Link
        href={sponsor.url || '#'}
        target="_blank"
        rel="noopener noreferrer"
        className={`group dark:to-gray-850 flex flex-col gap-4 rounded-xl border border-gray-200/60 bg-white p-6 transition-all duration-300 hover:border-gray-400 hover:shadow-xl hover:shadow-gray-200/50 dark:border-gray-700/40 dark:bg-gradient-to-br dark:from-gray-800 dark:hover:border-gray-600/50 dark:hover:shadow-xl dark:hover:shadow-black/30 ${tier.ring} ${tier.glow} `}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="relative h-20 w-20 flex-shrink-0 overflow-hidden rounded-lg bg-gradient-to-br from-gray-100 to-gray-50 dark:from-gray-700/60 dark:to-gray-800/40">
            {sponsor.imageUrl ? (
              <Image
                src={sponsor.imageUrl}
                alt={sponsor.name}
                fill
                className="object-contain p-2 transition-transform duration-300 group-hover:scale-110"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-3xl font-bold text-gray-300 dark:text-gray-500">
                {sponsor.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <span
            className={`inline-flex flex-shrink-0 items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold tracking-wider uppercase ${tier.badge}`}
          >
            <span className="text-base">{tier.icon}</span>
            {sponsor.sponsorType}
          </span>
        </div>

        <div className="flex-1">
          <h3 className="mb-1 text-lg font-bold text-gray-900 dark:text-white">{sponsor.name}</h3>
          {sponsor.description && (
            <p className="line-clamp-2 text-sm text-gray-600 dark:text-gray-300">
              {sponsor.description}
            </p>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-gray-200/50 pt-4 dark:border-gray-700/50">
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Learn more</span>
          <FaExternalLinkAlt className="h-4 w-4 text-gray-400 transition-all duration-200 group-hover:translate-x-1 group-hover:text-gray-600 dark:group-hover:text-gray-300" />
        </div>
      </Link>
    )
  }
  return (
    <Link
      href={sponsor.url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className={`group flex flex-col items-center justify-center rounded-lg border border-gray-200/80 bg-white p-5 text-center transition-all duration-200 hover:border-gray-300 hover:shadow-md dark:border-gray-700/50 dark:bg-gray-800/50 dark:hover:border-gray-600 dark:hover:bg-gray-800/80 ${tier.ring} `}
    >
      <div
        className={`relative mb-3 h-16 w-24 overflow-hidden rounded-md border border-gray-200/40 dark:border-gray-700/40 ${tier.logoBg}`}
      >
        {sponsor.imageUrl ? (
          <Image
            src={sponsor.imageUrl}
            alt={sponsor.name}
            fill
            className="object-contain p-1 transition-transform duration-200 group-hover:scale-110"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center text-center">
            <div className={`text-xl font-bold ${tier.logoText}`}>
              {sponsor.name
                .split(' ')
                .slice(0, 2)
                .map((w) => w.charAt(0))
                .join('')
                .toUpperCase()}
            </div>
            <div
              className={`mt-0.5 text-[9px] font-semibold tracking-wider uppercase ${tier.logoText} opacity-75`}
            >
              {sponsor.name.split(' ')[0].slice(0, 8)}
            </div>
          </div>
        )}
      </div>

      <h4 className="mb-2 line-clamp-2 text-sm font-semibold text-gray-900 dark:text-white">
        {sponsor.name}
      </h4>

      <span
        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[9px] font-bold tracking-wide uppercase ${tier.badge}`}
      >
        <span className="text-xs">{tier.icon}</span>
        {sponsor.sponsorType}
      </span>
    </Link>
  )
}

interface SponsorListProps {
  sponsors: SponsorInfo[]
  variant?: 'compact' | 'card'
  title?: string
}

export const SponsorList: React.FC<SponsorListProps> = ({ sponsors, variant = 'card', title }) => {
  if (!sponsors || sponsors.length === 0) return null

  return (
    <div>
      {title && (
        <div className="mb-4 flex items-center gap-2">
          <FaStar className="h-4 w-4 text-amber-500" />
          <h3 className="text-xs font-bold tracking-widest text-gray-600 uppercase dark:text-gray-400">
            {title}
          </h3>
        </div>
      )}
      <div
        className={
          variant === 'card'
            ? 'grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
            : 'flex flex-wrap items-center justify-center gap-4'
        }
      >
        {sponsors.map((sponsor) => (
          <div key={sponsor.key} className="w-full max-w-xs">
            <SponsorBadge sponsor={sponsor} variant={variant} />
          </div>
        ))}
      </div>
    </div>
  )
}

export default SponsorBadge
