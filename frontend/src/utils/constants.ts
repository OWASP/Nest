import { faGithub, faSlack, faBluesky, faLinkedin } from '@fortawesome/free-brands-svg-icons'
import type { Link } from 'types/link'
import type { Section } from 'types/section'

export const headerLinks: Link[] = [
  {
    text: 'Community',
    submenu: [
      { text: 'Chapters', href: '/chapters' },
      { text: 'Members', href: '/members' },
      { text: 'Organizations', href: '/organizations' },
      { text: 'Snapshots', href: '/snapshots' },
    ],
  },
  {
    text: 'Projects',
    href: '/projects',
  },
  {
    text: 'Contribute',
    href: '/contribute',
  },
  {
    text: 'About',
    href: '/about',
  },
]

export const footerIcons = [
  {
    icon: faBluesky,
    href: 'https://bsky.app/profile/nest.owasp.org',
    label: 'Bluesky',
  },
  {
    icon: faGithub,
    href: 'https://github.com/owasp/nest',
    label: 'GitHub',
  },
  {
    icon: faLinkedin,
    href: 'https://www.linkedin.com/groups/14656108/',
    label: 'LinkedIn',
  },
  {
    icon: faSlack,
    href: 'https://owasp.slack.com/archives/project-nest',
    label: 'Slack',
  },
]

export const footerSections: Section[] = [
  {
    title: 'OWASP Nest',
    links: [
      { text: 'About', href: '/about' },
      { text: 'Contribute', href: 'https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md' },
      {
        text: 'GSoC 2025',
        href: 'https://owasp.org/www-community/initiatives/gsoc/gsoc2025ideas#owasp-nest',
      },
      {
        text: 'Sponsor',
        href: 'https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest',
      },
    ],
  },
  {
    title: 'Resources',
    links: [
      { text: 'Chapters', href: '/chapters/' },
      {
        text: 'Contribute',
        href: '/contribute/',
      },
      { text: 'Committees', href: '/committees/' },
      { text: 'Projects', href: '/projects/' },
    ],
  },
  {
    title: 'Community',
    links: [
      { text: 'Community Content', href: 'https://owasp.org/www-community/' },
      { text: 'Google Summer of Code', href: 'https://owasp.org/gsoc' },
      {
        text: 'Start a Local Chapter',
        href: 'https://owasporg.atlassian.net/servicedesk/customer/portal/8/group/20/create/90?src=-1419759666',
      },
      {
        text: 'Start a New Project',
        href: 'https://owasporg.atlassian.net/servicedesk/customer/portal/7/create/70?src=-1419759666',
      },
    ],
  },
  {
    title: 'OWASP',
    links: [
      { text: 'About', href: 'https://owasp.org/about/' },
      { text: 'Contact', href: 'https://owasp.org/contact/' },
      { text: 'Events', href: 'https://owasp.glueup.com/organization/6727/events/' },
      { text: 'Team', href: 'https://owasp.org/corporate/' },
    ],
  },
]

export const tooltipStyle = {
  borderRadius: '8px',
  zIndex: 100,
}

export const themeToggleTooltip = {
  backgroundColor: '#28282B',
  color: 'white',
  fontSize: '0.7rem',
  borderRadius: '6px',
  padding: '3px 7px',
}

export const desktopViewMinWidth = 768
