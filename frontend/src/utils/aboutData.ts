import {
  faCodeBranch,
  faDesktop,
  faDatabase,
  faRobot,
  faChartLine,
  faCloud,
} from '@fortawesome/free-solid-svg-icons'

export const aboutText = [
  'OWASP Nest was originally created by Arkadii Yakovets (Ark) to simplify OWASP projects navigation. Built from scratch based on Ark’s vision and discussions with Starr Brown (Starr), the platform integrates structured system design into the OWASP ecosystem. The initial frontend, based on Vue.js, was introduced by Kateryna Golovanova (Kate), who later became the project co-leader due to her invaluable frontend and project management skills.',
  'Over time, OWASP Nest has expanded to address broader community needs, such as Google Summer of Code (GSoC) student guidance and contribution opportunities discovery. The platform, alongside NestBot, has become a central hub for OWASP projects, chapters, users, and aggregated contribution opportunities.',
  'The code is licensed under the MIT License, encouraging contributions while protecting the authors from legal claims. All OWASP Nest leaders are certified ISC2 professionals and OWASP members who adhere to the OWASP Code of Conduct.',
]

export const roadmap = [
  {
    title: 'Create OWASP Contribution Hub to centralize collaboration opportunities',
    issueLink: 'https://github.com/OWASP/Nest/issues/710',
    icon: faCodeBranch,
    description: 'Building a centralized platform for all OWASP contribution opportunities.',
    detailedDescription:
      'The Contribution Hub will serve as a single point of entry for new contributors to discover and engage with OWASP projects. It will feature project listings, help wanted issues, mentorship opportunities, and personalized contribution suggestions based on skill sets and interests.',
  },
  {
    title:
      'Design and launch the OWASP API for chapters, projects, committees, and other OWASP entities',
    issueLink: 'https://github.com/OWASP/Nest/issues/707',
    icon: faDesktop,
    description: 'Creating a unified API to access data across all OWASP resources.',
    detailedDescription:
      "The OWASP API will provide programmatic access to OWASP's ecosystem data, enabling developers to build applications and integrations that leverage OWASP resources. The API will follow REST principles, include comprehensive documentation, and support various authentication methods to ensure secure access.",
  },
  {
    title:
      'Develop OWASP Schema to standardize metadata for chapters, projects, and other entities',
    issueLink: 'https://github.com/OWASP/Nest/issues/709',
    icon: faDatabase,
    description: 'Standardizing data structure for consistent representation across the ecosystem.',
    detailedDescription:
      'The OWASP Schema project will define standardized data models for projects, chapters, events, and other OWASP entities. This standardization will ensure consistent data representation across systems, facilitate data exchange, and enable more efficient integration between OWASP platforms and tools.',
  },
  {
    title: 'Extend OWASP NestBot with AI agent/assistant capabilities',
    issueLink: 'https://github.com/OWASP/Nest/issues/908',
    icon: faRobot,
    description: 'Enhancing NestBot with advanced AI features to better assist the community.',
    detailedDescription:
      'The enhanced NestBot will incorporate machine learning models trained on OWASP resources to provide intelligent responses to community questions, suggest relevant resources, and assist with common tasks. The AI capabilities will include natural language understanding, personalized recommendations, and integration with various communication channels.',
  },
  {
    title: 'Implement OWASP Project Health Dashboard',
    issueLink: 'https://github.com/OWASP/Nest/issues/711',
    icon: faChartLine,
    description: 'Providing visibility into project activity, contributions, and overall health.',
    detailedDescription:
      'The Project Health Dashboard will offer comprehensive insights into the health and activity of OWASP projects through a visual interface. Metrics will include commit frequency, contributor growth, issue response time, release cadence, and community engagement metrics. The dashboard will help project leaders identify areas for improvement and showcase active projects to potential contributors.',
  },
  {
    title: 'Migrate OWASP Nest to Kubernetes',
    issueLink: 'https://github.com/OWASP/Nest/issues/706',
    icon: faCloud,
    description: 'Improving scalability and reliability through containerized deployment.',
    detailedDescription:
      'The migration to Kubernetes will involve containerizing all OWASP Nest services, implementing Helm charts for deployment, establishing CI/CD pipelines for automatic deployment, and configuring monitoring and logging systems. This will improve system reliability, enable easier scaling, and reduce infrastructure maintenance overhead.',
  },
]

export const technologies = [
  {
    section: 'Backend',
    tools: {
      Python: {
        icon: '/images/icons/python.svg',
        url: 'https://www.python.org/',
      },
      Django: {
        icon: '/images/icons/django.svg',
        url: 'https://www.djangoproject.com/',
      },
      PostgreSQL: {
        icon: '/images/icons/postgresql.svg',
        url: 'https://www.postgresql.org/',
      },
    },
  },
  {
    section: 'Frontend',
    tools: {
      Typescript: {
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
      Jest: {
        icon: '/images/icons/jest.svg',
        url: 'https://jestjs.io/',
      },
      PlayWright: {
        icon: '/images/icons/playwright.svg',
        url: 'https://playwright.dev/',
      },
      Pytest: {
        icon: '/images/icons/pytest.svg',
        url: 'https://docs.pytest.org/',
      },
    },
  },
  {
    section: 'Tools',
    tools: {
      Ansible: {
        icon: '/images/icons/ansible.svg',
        url: 'https://www.ansible.com/',
      },
      GitHub: {
        icon: '/images/icons/github.svg',
        url: 'https://www.github.com/',
      },
      Docker: {
        icon: '/images/icons/docker.svg',
        url: 'https://www.docker.com/',
      },
    },
  },
]
