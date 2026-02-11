import { FaMapMarkerAlt, FaUsers, FaBuilding, FaCamera } from 'react-icons/fa'

export const exploreCards = [
  {
    icon: FaMapMarkerAlt,
    title: 'Chapters',
    description: 'Discover local OWASP chapters worldwide',
    href: '/community/chapters',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
  },
  {
    icon: FaUsers,
    title: 'Members',
    description: 'Connect with community members',
    href: '/community/members',
    color: 'text-green-500',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
  },
  {
    icon: FaBuilding,
    title: 'Organizations',
    description: 'Explore OWASP organizations',
    href: '/community/organizations',
    color: 'text-purple-500',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20',
  },
  {
    icon: FaCamera,
    title: 'Snapshots',
    description: 'View community snapshots and highlights',
    href: '/community/snapshots',
    color: 'text-orange-500',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20',
  },
]

export const engagementWays = [
  {
    title: 'Join Local Chapters',
    description: 'Find and connect with OWASP chapters in your area to participate in local events and meetups.',
  },
  {
    title: 'Connect with Members',
    description: 'Network with security professionals, developers, and enthusiasts from around the world.',
  },
  {
    title: 'Contribute to Projects',
    description: 'Share your expertise by contributing to open-source security projects and initiatives.',
  },
  {
    title: 'Participate in Discussions',
    description: 'Join conversations, share knowledge, and learn from the global cybersecurity community.',
  },
]

export const journeySteps = [
  { label: 'Discover', description: 'Explore chapters, members, and organizations' },
  { label: 'Connect', description: 'Build relationships within the community' },
  { label: 'Participate', description: 'Join events and contribute to discussions' },
  { label: 'Contribute', description: 'Share your knowledge and expertise' },
]
