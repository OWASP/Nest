import { useEffect, useRef } from 'react'
import { SponsorType } from 'types/home'

interface MovingLogosProps {
  sponsors: SponsorType[]
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
              <a
                href={sponsor.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex h-full w-full flex-col items-center justify-center"
              >
                <div className="relative mb-4 flex h-16 w-full items-center justify-center">
                  {sponsor.imageUrl ? (
                    <img
                      src={sponsor.imageUrl}
                      alt={`${sponsor.name} logo`}
                      className="h-full w-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center"></div>
                  )}
                </div>
              </a>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-4 flex w-full flex-col items-center justify-center text-center text-sm text-muted-foreground">
        <p>
          These logos represent the corporate supporters of the OWASP Foundation, whose
          contributions fuel OWASP's security initiatives. Visit{' '}
          <a
            href="https://owasp.org/supporters/"
            className="font-medium text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            this page
          </a>{' '}
          to become an OWASP Foundation corporate supporter. If you're interested in sponsoring the
          OWASP Nest project ❤️{' '}
          <a
            href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
            className="font-medium text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            click here
          </a>
          .
        </p>
      </div>
    </div>
  )
}
