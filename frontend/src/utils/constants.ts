export interface Link {
    text: string;
    href: string;
    isSpan?: boolean;
  }

  export interface Section {
    title: string;
    links: Link[];
  }

  export const footerSections: Section[] = [
    {
      title: 'About OWASP',
      links: [
        { text: 'Our Mission', href: '#' },
        { text: 'Team', href: '#' },
        { text: 'Careers', href: '#' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { text: 'Contribute', href: 'https://nest.owasp.dev/projects/contribute/' },
        { text: 'Projects', href: 'https://nest.owasp.dev/projects/' },
        { text: 'Chapters', href: 'https://nest.owasp.dev/chapters/' },
      ],
    },
    {
      title: 'Community',
      links: [
        { text: 'Committees', href: 'https://nest.owasp.dev/committees/' },
        { text: 'Events', href: '#' },
        { text: 'Forum', href: '#' },
      ],
    },
    {
      title: 'Contact',
      links: [
        { text: 'Locations', href: '#', isSpan: true },
        { text: 'Support', href: '#' },
        { text: 'Contact Us', href: 'https://owasp.org/contact/' },
      ],
    },
  ];
