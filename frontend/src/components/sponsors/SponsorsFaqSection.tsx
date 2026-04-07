import { FaChevronDown } from 'react-icons/fa6'
import { OWASP_NEST_DONATE_URL } from 'utils/constants'

const FAQ = [
  {
    q: 'How do I become a corporate sponsor?',
    a: 'Use the "Apply to sponsor" form on this page. The OWASP Nest team reviews applications and will follow up with next steps, including recognition tier and logo placement.',
  },
  {
    q: 'How does sponsorship support Nest?',
    a: 'Sponsorship helps sustain infrastructure, security reviews, contributor programs, and ongoing development of the platform that connects people to OWASP projects and chapters.',
  },
  {
    q: 'Can I support Nest without a full sponsorship package?',
    a: (
      <>
        Yes. One-time and recurring gifts to the OWASP Foundation can be directed to the Nest project via the{' '}
        <a
          href={OWASP_NEST_DONATE_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="font-medium text-blue-600 underline-offset-2 hover:underline dark:text-blue-400"
        >
          official donate link
        </a>
        . Tax treatment depends on your jurisdiction and OWASP Foundation policies—consult a tax professional if needed.
      </>
    ),
  },
] as const

export default function SponsorsFaqSection() {
  return (
    <section className="mt-16 md:mt-24" aria-labelledby="sponsors-faq-heading">
      <h2
        id="sponsors-faq-heading"
        className="mx-auto max-w-xl text-center text-2xl font-semibold tracking-tight text-gray-900 dark:text-white md:text-3xl"
      >
        Frequently asked questions
      </h2>

      <div className="mx-auto mt-10 max-w-2xl divide-y divide-gray-200 dark:divide-gray-700">
        {FAQ.map(({ q, a }) => (
          <details
            key={q}
            className="group py-4 [&_summary::-webkit-details-marker]:hidden"
          >
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-left text-base font-medium text-gray-900 dark:text-gray-200">
              <span>{q}</span>
              <FaChevronDown
                className="h-4 w-4 shrink-0 text-gray-900 transition-transform duration-200 group-open:rotate-180 dark:text-white"
                aria-hidden
              />
            </summary>
            <div className="mt-3 pr-8 text-sm leading-relaxed text-gray-600 dark:text-gray-400">
              {a}
            </div>
          </details>
        ))}
      </div>
    </section>
  )
}
