export interface Link {
  text: string
  href: string
  isSpan?: boolean
}

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
    text: 'Committees',
    href: '/committees',
  },
]

export interface Section {
  title: string
  links: Link[]
}

export const footerSections: Section[] = [
  {
    title: 'About OWASP',
    links: [
      { text: 'Our Mission', href: 'https://owasp.org/about/' },
      { text: 'Team', href: 'https://owasp.org/corporate/#' },
      { text: 'Careers', href: 'https://owasp.org/careers/' },
    ],
  },
  {
    title: 'Resources',
    links: [
      {
        text: 'Contribute',
        href: 'https://nest.owasp.dev/projects/contribute/',
      },
      { text: 'Projects', href: 'https://nest.owasp.dev/projects/' },
      { text: 'Chapters', href: 'https://nest.owasp.dev/chapters/' },
    ],
  },
  {
    title: 'Community',
    links: [
      { text: 'Committees', href: 'https://nest.owasp.dev/committees/' },
      { text: 'Events', href: 'https://owasp.org/events/' },
      { text: 'Forum', href: 'https://owasp.org/www-community/' },
    ],
  },
  {
    title: 'Contact',
    links: [
      { text: 'Locations', href: 'https://www.meetup.com/pro/owasp/' },
      { text: 'Support', href: 'https://owasp.org/donate/' },
      { text: 'Contact Us', href: 'https://owasp.org/contact/' },
    ],
  },
]
