import type { KeyFeature, ProjectTimeline, GetInvolved, MissionContent } from 'types/about'

export const missionContent: MissionContent = {
  mission:
    'OWASP Nest is a comprehensive, community-first platform built to enhance collaboration and contribution across the OWASP community. Acting as a central hub, it helps users discover chapters and projects, find contribution opportunities, and connect with like-minded individuals based on their interests and expertise.',
  whoItsFor:
    "OWASP Nest is designed for developers, designers, technical writers, students, security professionals, and contributors of all backgrounds. Whether you're just starting out or a seasoned OSS veteran, OWASP Nest provides intuitive tools to help you engage meaningfully in the OWASP ecosystem.",
} as const

export const keyFeatures: KeyFeature[] = [
  {
    title: 'Advanced Community Search',
    description:
      'Search across the entire OWASP ecosystem - including chapters, projects, committees, members, and events - with precision and speed.',
  },
  {
    title: 'Comprehensive Project Directory',
    description:
      'Explore all OWASP projects in one place with powerful search and sorting tools to quickly find projects by their attributes, focus areas, or activity level.',
  },
  {
    title: 'Community Member Explorer',
    description:
      'Browse and connect with OWASP members worldwide, accessing profiles, roles, and expertise to foster meaningful collaboration.',
  },
  {
    title: 'Geo-Aware Chapter Discovery',
    description:
      'Discover local OWASP chapters based on your location, making it easy to connect with nearby communities and events.',
  },
  {
    title: 'AI-Powered Contribution Opportunities',
    description:
      'Find contribution opportunities tailored to your skills with AI-generated recommendations that highlight impactful ways to get involved.',
  },
  {
    title: 'OWASP Nest API',
    description:
      'Access OWASP entities programmatically via a REST API - enabling developers to integrate community, project, and chapter data into their own tools and applications.',
  },
]

export const getInvolvedContent: GetInvolved = {
  description:
    "OWASP Nest thrives thanks to community-driven contributions. Here's how you can make an impact:",
  ways: [
    'Code Contributions: fix bugs or build new features',
    'Code Review: improve quality by reviewing pull requests',
    'Community Engagement: join Slack discussions and provide feedback',
    'Documentation: create or enhance onboarding guides and tutorials',
    'Issue Reporting: report bugs or propose improvements',
  ],
  callToAction:
    'To get started, visit the [OWASP Nest Repository](https://github.com/OWASP/Nest), explore the [Contributing Guidelines](https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md), and review the [Code of Conduct](https://github.com/OWASP/Nest/blob/main/CODE_OF_CONDUCT.md).',
}
export const projectStory = [
  'OWASP Nest was originally created by Arkadii Yakovets to simplify OWASP projects navigation. Built from scratch based on Ark’s vision and discussions with Starr Brown, the platform integrates structured system design into the OWASP ecosystem. The initial frontend, based on Vue.js, was introduced by Kate Golovanova, who later became the project co-leader due to her invaluable frontend and project management skills.',
  'Over time, OWASP Nest has expanded to address broader community needs, such as Google Summer of Code (GSoC) student guidance and contribution opportunities discovery. The platform, alongside NestBot, has become a central hub for OWASP projects, chapters, users, and aggregated contribution opportunities.',
  'The code is licensed under the MIT License, encouraging contributions while protecting the authors from legal claims. All OWASP Nest leaders are certified ISC2 professionals and OWASP members who adhere to the OWASP Code of Conduct.',
]
export const projectTimeline: ProjectTimeline[] = [
  {
    title: 'Project Inception',
    description:
      'Initial brainstorming and vision by Arkadii Yakovets & Starr Brown to solve OWASP project navigation challenges.',
    year: 'August 2024',
  },
  {
    title: 'Backend Minimum Viable Product',
    description:
      'Backend foundations built by Arkadii Yakovets using Django and Docker. GitHub sync implemented for automated data updates.',
    year: 'August 2024',
  },
  {
    title: 'NestBot for Slack Community Integration',
    description:
      'A key feature allowing users to browse and search all OWASP projects effectively.',
    year: 'September 2024',
  },
  {
    title: 'Initial Frontend Development',
    description: 'Frontend initially developed by Kate Golovanova using Vue.js and Bootstrap.',
    year: 'September 2024',
  },
  {
    title: 'New React-based Frontend',
    description:
      'Started transitioning the frontend from Vue.js to React for better performance and scalability.',
    year: 'November 2024',
  },
  {
    title: 'NestBot Commands and Event Handlers Expansion',
    description:
      'Enhanced NestBot with advanced command processing and intelligent event handlers to improve user interaction efficiency.',
    year: 'January 2025',
  },
  {
    title: 'First Official Release and Production Launch',
    description:
      'We officially launched OWASP Nest to the public, inviting the community to explore and contribute.',
    year: 'February 2025',
  },
  {
    title: 'GSoC 2025 Participation',
    description: 'OWASP Nest accepted for Google Summer of Code 2025 as part of OWASP.',
    year: 'May 2025',
  },
  {
    title: 'OWASP Nest Sponsorship Program Launch',
    description:
      'We started sponsoring some interesting projects that have not made it to the GSoC 2025.',
    year: 'June 2025',
  },
  {
    title: 'OWASP Nest Sponsorship Program Expansion',
    description:
      'OWASP Nest expanded its Sponsorship Program to support ongoing project maintenance and new initiatives.',
    year: 'October 2025',
  },
  {
    title: 'Lab Level Promotion',
    description:
      "OWASP Nest promoted to Lab level, marking a significant milestone in the project's growth and maturity within the OWASP ecosystem.",
    year: 'October 2025',
  },
  {
    title: 'OWASP Nest API Hackathon',
    description:
      'We hosted a successful hackathon to encourage adoption and hands-on use of the OWASP Nest REST API.',
    year: 'November 2025',
  },
  {
    title: 'OWASP Nest Logo Introduction',
    description:
      "Introduced the official OWASP Nest logo as part of the project's branding and visual identity.",
    year: 'December 2025',
  },
]

export const technologies = [
  {
    section: 'Backend',
    tools: {
      python: {
        icon: '/images/icons/python.svg',
        url: 'https://www.python.org/',
      },
      django: {
        icon: '/images/icons/django.svg',
        url: 'https://www.djangoproject.com/',
      },
      postgreSQL: {
        icon: '/images/icons/postgresql.svg',
        url: 'https://www.postgresql.org/',
      },
    },
  },
  {
    section: 'Frontend',
    tools: {
      typescript: {
        icon: '/images/icons/typescript.svg',
        url: 'https://www.typescriptlang.org/',
      },
      'Next.js': {
        icon: '/images/icons/nextjs.svg',
        url: 'https://nextjs.org/',
      },
      'Tailwind CSS': {
        icon: '/images/icons/tailwindcss.svg',
        url: 'https://tailwindcss.com/',
      },
    },
  },
  {
    section: 'Tests',
    tools: {
      jest: {
        icon: '/images/icons/jest.svg',
        url: 'https://jestjs.io/',
      },
      playWright: {
        icon: '/images/icons/playwright.svg',
        url: 'https://playwright.dev/',
      },
      pytest: {
        icon: '/images/icons/pytest.svg',
        url: 'https://docs.pytest.org/',
      },
    },
  },
  {
    section: 'Tools',
    tools: {
      ansible: {
        icon: '/images/icons/ansible.svg',
        url: 'https://www.ansible.com/',
      },
      gitHub: {
        icon: '/images/icons/github.svg',
        url: 'https://www.github.com/',
      },
      docker: {
        icon: '/images/icons/docker.svg',
        url: 'https://www.docker.com/',
      },
    },
  },
]
