'use client'

import Link from 'next/link'
import { FaMapMarkerAlt } from 'react-icons/fa'
import {
  FaBuilding,
  FaChevronRight,
  FaFolder,
  FaHandshakeAngle,
  FaPeopleGroup,
  FaUsers,
} from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

const SLACK_CHANNEL_URL = 'https://owasp.slack.com/archives/project-nest'

const NAV_SECTIONS = [
  {
    title: 'Chapters',
    description: 'Find local OWASP chapters and connect with your community.',
    href: '/chapters',
    icon: FaMapMarkerAlt,
    color: 'text-green-500',
  },
  {
    title: 'Projects',
    description: 'Explore open-source security projects and contribute.',
    href: '/projects',
    icon: FaFolder,
    color: 'text-blue-500',
  },
  {
    title: 'Committees',
    description: 'OWASP committees driving security governance.',
    href: '/committees',
    icon: FaPeopleGroup,
    color: 'text-purple-500',
  },
  {
    title: 'Organizations',
    description: 'Browse OWASP organizations and their work.',
    href: '/organizations',
    icon: FaBuilding,
    color: 'text-orange-500',
  },
  {
    title: 'Members',
    description: 'Meet the people behind OWASP.',
    href: '/members',
    icon: FaUsers,
    color: 'text-teal-500',
  },
  {
    title: 'Contribute',
    description: 'Find issues and start contributing today.',
    href: '/contribute',
    icon: FaHandshakeAngle,
    color: 'text-pink-500',
  },
]

const CommunityPage = () => {
  return (
    <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        {/* Hero */}
        <div className="pb-4 pt-2 text-center">
          <div className="flex flex-col items-center gap-2">
            <h1 className="text-3xl font-medium tracking-tighter sm:text-5xl md:text-6xl">
              Community Hub
            </h1>
            <p className="text-muted-foreground max-w-[700px] md:text-xl">
              Your gateway into the OWASP community — explore chapters, projects, and people.
            </p>
          </div>
        </div>

        {/* Explore the Community */}
        <SecondaryCard
          title={
            <div className="flex items-center gap-2">
              <AnchorTitle title="Explore the Community" />
            </div>
          }
          className="overflow-hidden"
        >
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {NAV_SECTIONS.map((section) => (
              <Link
                key={section.title}
                href={section.href}
                className="group flex items-start gap-4 rounded-lg bg-gray-200 p-5 transition-all duration-300 hover:bg-blue-50 dark:bg-gray-700 dark:hover:bg-blue-950"
              >
                <div className="flex-shrink-0 pt-1">
                  <IconWrapper icon={section.icon} className={`h-6 w-6 ${section.color}`} />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-800 group-hover:text-blue-500 dark:text-gray-200">
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

        {/* Slack link */}
        <div className="mt-2 text-center">
          <Link
            href={SLACK_CHANNEL_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-blue-400 hover:text-blue-600"
          >
            Join the Slack channel
          </Link>
        </div>
      </div>
    </div>
  )
}

export default CommunityPage
