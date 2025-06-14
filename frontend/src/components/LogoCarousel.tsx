import Image from 'next/image'
import Link from 'next/link'
import { useEffect, useRef } from 'react'
import type { Sponsor } from 'types/home'

interface MovingLogosProps {
  sponsors: Sponsor[]
}

export default function MovingLogos({ sponsors }: MovingLogosProps) {
  const scrollerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollerRef.current) {
      const scrollContainer = scrollerRef.current
      scrollContainer.innerHTML += scrollContainer.innerHTML
    }
  }, [sponsors])

  return (
    <div>
      <div className="relative overflow-hidden py-2">
        <div
          ref={scrollerRef}
          className="flex w-full animate-scroll gap-6"
          style={{ animationDuration: `${sponsors.length * 2}s` }}
        >
          {sponsors.map((sponsor, index) => (
            <div
              key={`${sponsor.name}-${index}`}
              className="flex min-w-[220px] flex-shrink-0 flex-col items-center rounded-lg p-5"
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
                      alt={`${sponsor.name} logo`}
                      src={sponsor.imageUrl}
                      style={{ objectFit: 'contain' }}
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center"></div>
                  )}
                </div>
              </Link>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-4 flex w-full flex-col items-center justify-center text-center text-sm text-muted-foreground">
        <p>
          These logos represent the corporate supporters, whose contributions fuel OWASP Foundation
          security initiatives. Visit{' '}
          <Link
            href="https://owasp.org/supporters/"
            className="font-medium text-primary hover:underline"
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
            className="font-medium text-primary hover:underline"
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
