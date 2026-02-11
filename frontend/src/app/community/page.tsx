'use client'

import { useQuery } from '@apollo/client/react'
import millify from 'millify'
import Link from 'next/link'
import { FaMapMarkerAlt } from 'react-icons/fa'
import {
  FaBuilding,
  FaChevronRight,
  FaFolder,
  FaHandshakeAngle,
  FaPeopleGroup,
  FaUsers,
  FaTag,
} from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { IconWrapper } from 'wrappers/IconWrapper'
import { GetMainPageDataDocument } from 'types/__generated__/homeQueries.generated'
import { Release as ReleaseType } from 'types/release'
import AnchorTitle from 'components/AnchorTitle'
import CommunityContributorsList from 'components/CommunityContributorsList'
import LoadingSpinner from 'components/LoadingSpinner'
import Release from 'components/Release'
import SecondaryCard from 'components/SecondaryCard'

const NAV_SECTIONS = [
  {
    title: 'Chapters',
    description: 'Find local OWASP chapters and connect with your community.',
    href: '/chapters',
    icon: FaMapMarkerAlt,
    color: 'text-gray-900 dark:text-gray-100',
  },
  {
    title: 'Projects',
    description: 'Explore open-source security projects and contribute.',
    href: '/projects',
    icon: FaFolder,
    color: 'text-gray-900 dark:text-gray-100',
  },
  {
    title: 'Committees',
    description: 'OWASP committees driving security governance.',
    href: '/committees',
    icon: FaPeopleGroup,
    color: 'text-gray-900 dark:text-gray-100',
  },
  {
    title: 'Organizations',
    description: 'Browse OWASP organizations and their work.',
    href: '/organizations',
    icon: FaBuilding,
    color: 'text-gray-900 dark:text-gray-100',
  },
  {
    title: 'Members',
    description: 'Meet the people behind OWASP.',
    href: '/members',
    icon: FaUsers,
    color: 'text-gray-900 dark:text-gray-100',
  },
  {
    title: 'Contribute',
    description: 'Find issues and start contributing today.',
    href: '/contribute',
    icon: FaHandshakeAngle,
    color: 'text-gray-900 dark:text-gray-100',
  },
]

const CommunityPage = () => {
  const { data, loading, error } = useQuery(GetMainPageDataDocument, {
    variables: {
      recentReleasesLimit: 10,
      topContributorsLimit: 10,
    },
  })

  if (loading) return <LoadingSpinner />
  if (error)
    return <div className="p-8 text-center text-red-500">Error loading community data.</div>

  const statsOverview = data?.statsOverview

  const stats = [
    {
      icon: FaUsers,
      value: millify(statsOverview?.contributorsStats || 0),
      label: 'Contributors',
      color: 'text-gray-900 dark:text-gray-100',
      bg: 'bg-gray-100 dark:bg-gray-800',
    },
    {
      icon: FaMapMarkerAlt,
      value: millify(statsOverview?.activeChaptersStats || 0),
      label: 'Active Chapters',
      color: 'text-gray-900 dark:text-gray-100',
      bg: 'bg-gray-100 dark:bg-gray-800',
    },
    {
      icon: FaFolder,
      value: millify(statsOverview?.activeProjectsStats || 0),
      label: 'Active Projects',
      color: 'text-gray-900 dark:text-gray-100',
      bg: 'bg-gray-100 dark:bg-gray-800',
    },
  ]

  return (
    <div className="mt-2 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        {/* Hero */}
        <div className="pt-2 pb-8 text-center">
          <div className="flex flex-col items-center gap-2">
            <h1 className="text-3xl font-medium tracking-tighter sm:text-5xl md:text-6xl">
              Community Hub
            </h1>
            <p className="text-muted-foreground max-w-[700px] md:text-xl">
              Your gateway into the OWASP community — explore chapters, projects, and people.
            </p>
          </div>
        </div>

        {/* Explore the Community (Resources) */}
        <div className="mb-12">
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
        </div>

        {/* Stats Grid */}
        <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-3">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
            >
              <div className="flex items-center gap-4">
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-full ${stat.bg} ${stat.color}`}
                >
                  <stat.icon className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    {stat.label}
                  </p>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</h3>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3 lg:grid-cols-3">
          {/* Main Content: Recent Releases (Renamed from Activity Feed) */}
          <div className="md:col-span-2">
            <SecondaryCard
              icon={FaTag}
              title={<AnchorTitle title="Recent Releases" />}
              className="!mb-0 h-full"
            >
              <div className="mb-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Latest updates from across the OWASP ecosystem.
                </p>
              </div>
              <div className="flex flex-col gap-4">
                {data?.recentReleases?.slice(0, 6).map((release, index) => (
                  <Release
                    key={release.tagName}
                    release={release as ReleaseType}
                    index={index}
                    showAvatar={true}
                  />
                ))}
              </div>
              <div className="mt-4 text-center">
                <Link
                  href="/projects"
                  className="font-medium text-blue-500 hover:text-blue-600 hover:underline"
                >
                  View all recent releases &rarr;
                </Link>
              </div>
            </SecondaryCard>
          </div>

          {/* Sidebar: Top Contributors (Spotlight Removed) */}
          <div className="md:col-span-1">
            <CommunityContributorsList
              contributors={data?.topContributors || []}
              icon={HiUserGroup}
              maxInitialDisplay={10}
              title="Top Contributors"
              getUrl={(login: string) => `/members/${login}`}
              className="!mb-0 h-full"
            />
          </div>
        </div>

        {/* Quick Links */}
        <div className="border-t border-gray-200 pt-5 text-center dark:border-gray-800">
          <p className="mb-1 text-gray-500">Want to get more involved?</p>
          <div className="flex justify-center gap-2 text-sm font-medium text-gray-500">
            <Link href="https://github.com/owasp" className="hover:text-blue-500 hover:underline">
              Github
            </Link>
            <span>&middot;</span>
            <Link href="/members" className="hover:text-blue-500 hover:underline">
              Members
            </Link>
            <span>&middot;</span>
            <Link href="/organizations" className="hover:text-blue-500 hover:underline">
              Organizations
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CommunityPage
