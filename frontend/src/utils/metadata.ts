import { PageMetadata } from 'types/seo'

interface MetadataConfig {
  home: PageMetadata
  projects: PageMetadata
  committees: PageMetadata
  chapters: PageMetadata
  users: PageMetadata
  projectContribute: PageMetadata
}

export const METADATA_CONFIG: MetadataConfig = {
  home: {
    title: 'Home',
    description:
      'OWASP Nest is a comprehensive platform designed to enhance collaboration and contribution within the OWASP community.',
    keywords: ['OWASP', 'security', 'open source', 'web security', 'application security'],
    type: 'website',
  },
  projects: {
    title: 'Projects',
    description: 'Explore OWASP projects and contribute to open source security initiatives.',
    keywords: ['OWASP projects', 'security projects', 'open source security'],
    type: 'website',
  },
  committees: {
    title: 'Committees',
    description: 'Learn about OWASP committees and their initiatives in web security.',
    keywords: ['OWASP committees', 'security committees', 'web security governance'],
    type: 'website',
  },
  chapters: {
    title: 'Chapters',
    description: 'Find OWASP chapters worldwide and connect with local security communities.',
    keywords: ['OWASP chapters', 'local chapters', 'security community'],
    type: 'website',
  },
  users: {
    title: 'Community',
    description: 'Meet OWASP community members and contributors.',
    keywords: ['OWASP community', 'security professionals', 'contributors'],
    type: 'website',
  },
  projectContribute: {
    title: 'Contribute',
    description: 'Contribute to OWASP projects and initiatives.',
    keywords: ['OWASP projects', 'contribute', 'open source security'],
    type: 'website',
  },
}
