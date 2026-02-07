import Image from 'next/image'
import Link from 'next/link'
import type { Sponsor } from 'types/home'

interface MovingLogosProps {
  readonly sponsors: Sponsor[]
}

export default function MovingLogos({ sponsors }: Readonly<MovingLogosProps>) {
  const animationDuration = `${Math.max(sponsors.length, 1) * 3}s`

  const renderSponsorCard = (sponsor: Sponsor, index: number, keySuffix: string) => {
    const keyBase = sponsor.id
      ? `${sponsor.id}-${index}`
      : `${sponsor.url || sponsor.name || 'sponsor'}-${index}`

    return (
      <div
        key={`logo-carousel-${keyBase}-${keySuffix}`}
        className="flex shrink-0 items-center justify-center"
      >
        <Link href={sponsor.url} target="_blank" rel="noopener noreferrer">
          <div className="flex h-20 w-44 items-center justify-center rounded-lg bg-white px-3 py-1 shadow-md">
            {sponsor.imageUrl ? (
              <Image
                alt={sponsor.name ? `${sponsor.name}'s logo` : 'Sponsor logo'}
                className="h-full w-full object-contain"
                height={72}
                src={sponsor.imageUrl}
                width={168}
              />
            ) : (
              <span className="text-sm text-gray-400">{sponsor.name}</span>
            )}
          </div>
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div className="group relative overflow-hidden py-2">
        <div
          className="animate-scroll flex w-max gap-6 group-hover:[animation-play-state:paused]"
          style={{ animationDuration }}
        >
          {sponsors.map((sponsor, index) => renderSponsorCard(sponsor, index, 'a'))}
          {sponsors.map((sponsor, index) => renderSponsorCard(sponsor, index, 'b'))}
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
