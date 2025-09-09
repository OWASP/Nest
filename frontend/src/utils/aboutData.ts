import type {
  KeyFeature,
  ProjectHistory,
  GetInvolved,
  MissionContent,
} from 'types/about'

export const aboutText = [
  'OWASP Nest was originally created by Arkadii Yakovets (Ark) to simplify OWASP projects navigation. Built from scratch based on Ark’s vision and discussions with Starr Brown (Starr), the platform integrates structured system design into the OWASP ecosystem. The initial frontend, based on Vue.js, was introduced by Kateryna Golovanova (Kate), who later became the project co-leader due to her invaluable frontend and project management skills.',
  'Over time, OWASP Nest has expanded to address broader community needs, such as Google Summer of Code (GSoC) student guidance and contribution opportunities discovery. The platform, alongside NestBot, has become a central hub for OWASP projects, chapters, users, and aggregated contribution opportunities.',
  'The code is licensed under the MIT License, encouraging contributions while protecting the authors from legal claims. All OWASP Nest leaders are certified ISC2 professionals and OWASP members who adhere to the OWASP Code of Conduct.',
]

export const missionContent: MissionContent = {
  mission:
    'OWASP Nest is a comprehensive platform built to enhance collaboration and streamline contributions across the OWASP community. Acting as a central hub, it helps users discover projects, find contribution opportunities, and connect with like-minded individuals based on their interests and expertise.',
  whoItsFor:
    "OWASP Nest is designed for developers, designers, technical writers, students, security professionals, and contributors of all backgrounds. Whether you're just starting out or a seasoned OSS veteran, Nest provides intuitive tools to help you engage meaningfully in the OWASP ecosystem.",
} as const

export const keyFeatures: KeyFeature[] = [
  {
    title: 'Advanced Search Capabilities',
    description:
      'Easily filter and explore projects or issues using keywords, tags, and contributor preferences.',
  },
  {
    title: 'Slack Integration',
    description:
      'Stay connected through a Slack bot that delivers updates and supports both direct and channel messaging.',
  },
  {
    title: 'OWASP Chapters Proximity Page',
    description: 'Discover and connect with nearby OWASP chapters for local engagement.',
  },
  {
    title: 'AI-Generated Insights',
    description:
      'Benefit from AI-powered summaries and actionable suggestions for tackling project issues.',
  },
]

export const getInvolvedContent: GetInvolved = {
  description:
    "OWASP Nest thrives thanks to community-driven contributions. Here's how you can make an impact:",
  ways: [
    'Code Contributions – Fix bugs or build new features',
    'Code Review – Improve quality by reviewing pull requests',
    'Documentation – Create or enhance onboarding guides and tutorials',
    'Issue Reporting – Report bugs or propose improvements',
    'Community Engagement – Join Slack discussions and provide feedback',
  ],
  callToAction:
  'To get started, visit the [OWASP Nest Repository](https://github.com/OWASP/Nest), explore the [Contributing Guidelines](https://github.com/OWASP/Nest/blob/main/CONTRIBUTING.md), and review the [Code of Conduct](https://github.com/OWASP/Nest/blob/main/CODE_OF_CONDUCT.md).',
}

export const projectHistory: ProjectHistory[] = [
  {
    title: 'Project Inception',
    description:
      'Initial brainstorming and vision by Arkadii Yakovets (Ark) & Starr Brown to solve OWASP project navigation challenges',
    year: 'Jan 2023',
  },
  {
    title: 'Backend MVP',
    description:
      'Backend foundations built using Python, Django, DRF with AI capabilities integrated',
    year: 'Mar 2023',
  },
  {
    title: 'Frontend Development',
    description:
      'Frontend initially developed by Kateryna Golovanova (Kate) using Vue.js, later transitioned to React',
    year: 'Sep 2024',
  },
  {
    title: 'Platform Integrations',
    description: 'Slack & Algolia integrations implemented for enhanced user experience',
    year: 'Nov 2024',
  },
  {
    title: 'GSoC Integration',
    description: 'Scaled to support Google Summer of Code and streamline contributor onboarding',
    year: 'Dec 2024',
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
