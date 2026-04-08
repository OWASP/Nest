import Link from 'next/link'
import { FaRegHeart } from 'react-icons/fa'
import { FaFlask, FaShieldHalved } from 'react-icons/fa6'

const SHOWCASE = [
  {
    badge: 'Nest',
    title: 'A community hub for OWASP projects, chapters, and contributors',
    description:
      'Search and filter initiatives, follow contribution opportunities, and stay close to chapters and Slack, all in one place.',
    href: '/',
    cta: 'Explore Nest',
    icon: FaRegHeart,
  },
  {
    badge: 'ZAP',
    title: "The world's most widely used web application security scanner",
    description:
      'Free and open source tooling maintained by a global community, helping teams find issues early in development.',
    href: 'https://owasp.org/www-project-zap/',
    cta: 'View OWASP ZAP',
    external: true,
    icon: FaShieldHalved,
  },
  {
    badge: 'Juice Shop',
    title: 'Hands-on training with a modern, intentionally vulnerable web app',
    description:
      'Practice offensive security safely in a realistic stack—used in workshops, capture-the-flag events, and self-paced learning.',
    href: 'https://owasp.org/www-project-juice-shop/',
    cta: 'View Juice Shop',
    external: true,
    icon: FaFlask,
  },
] as const

export default function SponsorsOpenSourceShowcase() {
  return (
    <section className="mt-16 md:mt-20" aria-labelledby="sponsors-showcase-heading">
      <h2
        id="sponsors-showcase-heading"
        className="mx-auto max-w-3xl text-center text-2xl font-semibold tracking-tight text-gray-900 md:text-3xl dark:text-white"
      >
        The web depends on open source—OWASP helps secure it everywhere
      </h2>

      <div className="mt-10 grid gap-6 md:grid-cols-3 md:gap-8">
        {SHOWCASE.map(({ badge, title, description, href, cta, external, icon: Icon }) => {
          const inner = (
            <>
              <div className="mb-5 flex items-start justify-between gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-700 dark:text-gray-300">
                  <Icon className="h-5 w-5" aria-hidden />
                </span>
                <span className="rounded-full border border-gray-300 px-2.5 py-0.5 text-xs font-medium text-gray-800 dark:border-gray-600 dark:text-gray-200">
                  {badge}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-gray-600 dark:text-gray-400">
                {description}
              </p>
              <span className="mt-auto inline-flex items-center gap-1 pt-5 text-sm font-medium whitespace-nowrap text-blue-600 dark:text-blue-400">
                {cta}
                <span aria-hidden className="translate-y-px">
                  &rsaquo;
                </span>
              </span>
            </>
          )

          const cardClass =
            'flex h-full flex-col rounded-2xl bg-gray-50 p-6 transition-colors hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 sm:p-7'

          if (external) {
            return (
              <a
                key={badge}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className={cardClass}
              >
                {inner}
              </a>
            )
          }

          return (
            <Link key={badge} href={href} className={cardClass}>
              {inner}
            </Link>
          )
        })}
      </div>
    </section>
  )
}
