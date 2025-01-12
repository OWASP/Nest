import { Link } from 'types/link'
import { Section } from 'types/section'

export const headerLinks: Link[] = [
  {
    text: 'Contribute',
    href: '/projects/contribute',
  },
  {
    text: 'Projects',
    href: '/projects',
  },
  {
    text: 'Chapters',
    href: '/chapters',
  },
  {
    text: 'Community',
    href: '/community/users',
  },
]

export const footerSections: Section[] = [
  {
    title: 'OWASP Nest',
    links: [
      { text: 'About', href: 'https://github.com/OWASP/Nest?tab=readme-ov-file#owasp-nest' },
      { text: 'Contact', href: 'https://owasp.slack.com/messages/project-nest' },
      { text: 'Contribute', href: 'https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md' },
      { text: 'Leaders', href: 'https://github.com/OWASP/Nest?tab=readme-ov-file#leaders' },
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
        href: '/projects/contribute/',
      },
      { text: 'Committees', href: '/committees/' },
      { text: 'Projects', href: '/projects/' },
    ],
  },
  {
    title: 'Community',
    links: [
      { text: 'Community Content', href: 'https://owasp.org/www-community/' },
      { text: 'Google Summer of Code', href: 'https://owasp.org/gsoc/gsoc2024' },
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
      { text: 'Membership', href: 'https://owasp.glueup.com/organization/6727/memberships/' },
      { text: 'Team', href: 'https://owasp.org/corporate/' },
    ],
  },
]

export const tooltipStyle = {
  borderRadius: '8px',
  zIndex: 100,
}
