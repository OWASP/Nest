'use client'

import Link from 'next/link'
import { FaArrowRight, FaSlack, FaChevronRight } from 'react-icons/fa'
import { IconWrapper } from 'wrappers/IconWrapper'
import { exploreCards as NAV_SECTIONS, engagementWays, journeySteps } from 'utils/communityData'
import AnchorTitle from 'components/AnchorTitle'
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
            Explore the vibrant OWASP community. Connect with{' '}
            <Link href="/chapters" className="text-blue-500 hover:underline">
              Chapters
            </Link>
            ,{' '}
            <Link href="/members" className="text-blue-500 hover:underline">
              Members
            </Link>
            , and{' '}
            <Link href="/organizations" className="text-blue-500 hover:underline">
              Organizations
            </Link>{' '}
            around the world at your fingertips. Discover opportunities to engage, learn, and
            contribute.
          </p>
        </div>

        {/* Explore Community Section */}
        <SecondaryCard
          title={
            <div className="flex items-center gap-2">
              <AnchorTitle title="Explore Resources" />
            </div>
          }
          className="overflow-hidden"
        >
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {NAV_SECTIONS.map((section) => (
              <Link
                key={section.title}
                href={section.href}
                className="group flex items-start gap-4 rounded-lg bg-gray-200 p-5 transition-all duration-300 hover:bg-blue-100 dark:bg-gray-700 dark:hover:bg-gray-600"
              >
                <div className="flex-shrink-0 pt-1">
                  <IconWrapper icon={section.icon} className={`h-6 w-6 ${section.color}`} />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-800 dark:text-gray-200">
                    {section.title}
                    <FaChevronRight className="h-3 w-3 transform transition-transform group-hover:translate-x-1" />
                  </h3>
                  <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    {section.description}
                  </p>
                </div>
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
            there&apos;s a place for you here. Start by{' '}
            <Link href="/contribute" className="text-blue-500 hover:underline">
              contributing to a project
            </Link>
            .
          </p>
        </SecondaryCard>
      </div>
    </div>
  )
}
