import Image from 'next/image'
import Link from 'next/link'
import type { Sponsor } from 'types/home'

interface MovingLogosProps {
  readonly sponsors: Sponsor[]
}

export default function MovingLogos({ sponsors }: Readonly<MovingLogosProps>) {
  // Keep duration behavior stable even when sponsors is empty.
  const animationDurationSeconds = Math.max(sponsors.length, 1) * 2

  const renderSponsorCard = (sponsor: Sponsor, index: number, keySuffix: string) => {
    // Include `index` to guarantee uniqueness even if `sponsor.id` repeats (e.g. in tests).
    const keyBase = sponsor.id
      ? `${sponsor.id}-${index}`
      : `${sponsor.url || sponsor.name || 'sponsor'}-${index}`

    return (
      <div
        key={['logo-carousel', keyBase, keySuffix ?? ''].filter(Boolean).join('-')}
        className="flex min-w-[220px] shrink-0 flex-col items-center rounded-lg p-5"
      >
        <Link
          href={sponsor.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex h-full w-full flex-col items-center justify-center"
        >
          <div className="relative mb-4 flex h-16 w-full items-center justify-center">
            {sponsor.imageUrl ? (
              <Image
                fill
                alt={sponsor.name ? `${sponsor.name}'s logo` : 'Sponsor logo'}
                src={sponsor.imageUrl}
                style={{ objectFit: 'contain' }}
              />
            ) : (
              <span className="sr-only">{sponsor.name}</span>
            )}
          </div>
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="relative overflow-hidden py-2">
        <div
          className="animate-scroll flex w-full gap-6"
          style={{ animationDuration: `${animationDurationSeconds}s` }}
        >
          {sponsors.map((sponsor, index) => renderSponsorCard(sponsor, index, ''))}
          {sponsors.map((sponsor, index) => renderSponsorCard(sponsor, index, 'loop'))}
        </div>
      </div>
      <div className="text-muted-foreground mt-4 flex w-full flex-col items-center justify-center text-center text-sm">
        <p>
          These logos represent the corporate supporters, whose contributions fuel OWASP Foundation
          security initiatives. Visit{' '}
          <Link
            href="https://owasp.org/supporters/"
            className="text-primary font-medium hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            this page
          </Link>{' '}
          to become a corporate supporter.
        </p>
        <p>
          If you're interested in sponsoring the OWASP Nest project ❤️{' '}
          <Link
            href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
            className="text-primary font-medium hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            click here
          </Link>
          .
        </p>
      </div>
    </div>
  )
}
