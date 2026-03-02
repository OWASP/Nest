import {
  FaBuilding,
  FaFolder,
  FaHandshakeAngle,
  FaLocationDot,
  FaPeopleGroup,
  FaUsers,
} from 'react-icons/fa6'

export const exploreCards = [
  {
    title: 'Chapters',
    description: 'Find local OWASP chapters and connect with your community.',
    href: '/chapters',
    icon: FaLocationDot,
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

export const engagementWays = [
  {
    title: 'Join Local Chapters',
    description:
      'Find and connect with OWASP chapters in your area to participate in local events and meetups.',
  },
  {
    title: 'Connect with Members',
    description:
      'Network with security professionals, developers, and enthusiasts from around the world.',
  },
  {
    title: 'Contribute to Projects',
    description:
      'Share your expertise by contributing to open-source security projects and initiatives.',
  },
  {
    title: 'Participate in Discussions',
    description:
      'Join conversations, share knowledge, and learn from the global cybersecurity community.',
  },
]

export const journeySteps = [
  { label: 'Discover', description: 'Explore chapters, members, and organizations' },
  { label: 'Connect', description: 'Build relationships within the community' },
  { label: 'Participate', description: 'Join events and contribute to discussions' },
  { label: 'Contribute', description: 'Share your knowledge and expertise' },
]
