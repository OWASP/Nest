'use client'
import Link from 'next/link'
import { FaArrowRight, FaSlack } from 'react-icons/fa'
import { exploreCards, engagementWays, journeySteps } from 'utils/communityData'
import SecondaryCard from 'components/SecondaryCard'

export default function CommunityPage() {
  return (
    <div className="min-h-screen w-full px-8 pt-24 pb-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
            OWASP Community
          </h1>
          <p className="mx-auto mb-8 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
            Explore the vibrant OWASP community. Connect with chapters, members, and organizations
            around the world. Discover opportunities to engage, learn, and contribute.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/chapters"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-600"
            >
              Explore Chapters
              <FaArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/members"
              className="inline-flex items-center gap-2 rounded-lg border-2 border-blue-500 px-6 py-3 font-semibold text-blue-500 transition-colors hover:bg-blue-50 dark:hover:bg-blue-900/20"
            >
              Meet Members
              <FaArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>

        {/* Explore Community Section */}
        <SecondaryCard title="Explore Community">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {exploreCards.map((card) => (
              <Link
                key={card.title}
                href={card.href}
                className="group rounded-lg border-2 border-gray-200 bg-white p-6 transition-all hover:scale-105 hover:border-blue-400 hover:shadow-lg dark:border-gray-700 dark:bg-gray-800 dark:hover:border-blue-500"
              >
                <div
                  className={`mb-4 inline-flex rounded-lg p-3 ${card.bgColor} transition-transform group-hover:scale-110`}
                >
                  <card.icon className={`h-6 w-6 ${card.color}`} />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {card.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{card.description}</p>
              </Link>
            ))}
          </div>
        </SecondaryCard>

        {/* Ways to Engage Section */}
        <SecondaryCard title="Ways to Engage">
          <div className="grid gap-6 md:grid-cols-2">
            {engagementWays.map((way) => (
              <div key={way.title} className="rounded-lg bg-gray-200 p-5 dark:bg-gray-700">
                <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {way.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{way.description}</p>
              </div>
            ))}
          </div>
        </SecondaryCard>

        {/* Community Journey Section */}
        <SecondaryCard title="Your Community Journey">
          <div className="relative">
            {/* Desktop view - horizontal */}
            <div className="hidden items-center justify-between md:flex">
              {journeySteps.map((step, idx) => (
                <div key={step.label} className="flex flex-1 items-center">
                  <div className="flex flex-col items-center text-center">
                    <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-blue-500 text-xl font-bold text-white">
                      {idx + 1}
                    </div>
                    <h3 className="mb-1 text-lg font-semibold">{step.label}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{step.description}</p>
                  </div>
                  {idx < journeySteps.length - 1 && (
                    <div className="mx-4 flex-1 border-t-2 border-dashed border-gray-400" />
                  )}
                </div>
              ))}
            </div>

            {/* Mobile view - vertical */}
            <div className="flex flex-col gap-6 md:hidden">
              {journeySteps.map((step, idx) => (
                <div key={step.label} className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-500 text-lg font-bold text-white">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="mb-1 text-lg font-semibold">{step.label}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </SecondaryCard>

        {/* Join the Community Section */}
        <SecondaryCard title="Join the Community">
          <div className="mx-auto max-w-2xl text-center">
            <div className="mb-6 inline-flex rounded-full bg-blue-50 p-4 dark:bg-blue-900/20">
              <FaSlack className="h-8 w-8 text-blue-500" aria-hidden="true" />
            </div>
            <p className="mb-8 text-lg text-gray-600 dark:text-gray-400">
              Connect with fellow security professionals, ask questions, share ideas, and
              collaborate with the global OWASP community on Slack.
            </p>
            <a
              href="https://owasp.org/slack/invite"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-500 px-8 py-3 text-lg font-semibold text-white transition-colors hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none dark:focus:ring-offset-gray-800"
              aria-label="Join OWASP Community Slack workspace"
            >
              Join Slack
              <FaArrowRight className="h-5 w-5" aria-hidden="true" />
            </a>
          </div>
        </SecondaryCard>

        {/* Final Call to Action */}
        <SecondaryCard className="text-center">
          <h2 className="mb-4 text-3xl font-bold">Ready to Get Involved?</h2>
          <p className="mb-8 text-lg text-gray-600 dark:text-gray-400">
            Join thousands of security professionals making a difference in the OWASP community.
            Whether you&apos;re just starting out or you&apos;re an experienced contributor,
            there&apos;s a place for you here.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/chapters"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-3 font-bold text-white transition-colors hover:bg-blue-600"
            >
              Find Your Chapter
              <FaArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/members"
              className="inline-flex items-center gap-2 rounded-lg bg-green-500 px-6 py-3 font-bold text-white transition-colors hover:bg-green-600"
            >
              Connect with Members
              <FaArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/contribute"
              className="inline-flex items-center gap-2 rounded-lg border-2 border-blue-500 px-6 py-3 font-bold text-blue-500 transition-colors hover:bg-blue-50 dark:hover:bg-blue-900/20"
            >
              Start Contributing
              <FaArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </SecondaryCard>
      </div>
    </div>
  )
}
