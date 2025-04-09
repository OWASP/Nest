export const aboutText = [
  'OWASP Nest was originally created by Arkadii Yakovets (Ark) to simplify OWASP projects navigation. Built from scratch based on Ark’s vision and discussions with Starr Brown (Starr), the platform integrates structured system design into the OWASP ecosystem. The initial frontend, based on Vue.js, was introduced by Kateryna Golovanova (Kate), who later became the project co-leader due to her invaluable frontend and project management skills.',
  'Over time, OWASP Nest has expanded to address broader community needs, such as Google Summer of Code (GSoC) student guidance and contribution opportunities discovery. The platform, alongside NestBot, has become a central hub for OWASP projects, chapters, users, and aggregated contribution opportunities.',
  'The code is licensed under the MIT License, encouraging contributions while protecting the authors from legal claims. All OWASP Nest leaders are certified ISC2 professionals and OWASP members who adhere to the OWASP Code of Conduct.',
]

export const roadmap = [
  {
    title: 'Create OWASP Contribution Hub to centralize collaboration opportunities',
    issueLink: 'https://github.com/OWASP/Nest/issues/710',
  },
  {
    title:
      'Design and launch the OWASP API for chapters, projects, committees, and other OWASP entities',
    issueLink: 'https://github.com/OWASP/Nest/issues/707',
  },
  {
    title:
      'Develop OWASP Schema to standardize metadata for chapters, projects, and other entities',
    issueLink: 'https://github.com/OWASP/Nest/issues/709',
  },
  {
    title: 'Extend OWASP NestBot with AI agent/assistant capabilities',
    issueLink: 'https://github.com/OWASP/Nest/issues/908',
  },
  {
    title: 'Implement OWASP Project Health Dashboard',
    issueLink: 'https://github.com/OWASP/Nest/issues/711',
  },
  {
    title: 'Migrate OWASP Nest to Kubernetes',
    issueLink: 'https://github.com/OWASP/Nest/issues/706',
  },
]

export const technologies = [
  {
    section: 'Backend',
    tools: {
      Python: {
        icon: '/icons/Python.svg',
        url: 'https://www.python.org/',
      },
      Django: {
        icon: '/icons/Django.svg',
        url: 'https://www.djangoproject.com/',
      },
      PostgreSQL: {
        icon: '/icons/PostgresSQL.svg',
        url: 'https://www.postgresql.org/',
      },
    },
  },
  {
    section: 'Frontend',
    tools: {
      Typescript: {
        icon: '/icons/TypeScript.svg',
        url: 'https://www.typescriptlang.org/',
      },
      React: {
        icon: '/icons/React.svg',
        url: 'https://reactjs.org/',
      },
      'Tailwind CSS': {
        icon: '/icons/TailwindCSS.svg',
        url: 'https://tailwindcss.com/',
      },
    },
  },
  {
    section: 'Tests',
    tools: {
      Jest: {
        icon: '/icons/Jest.svg',
        url: 'https://jestjs.io/',
      },
      PlayWright: {
        icon: '/icons/Playwright.svg',
        url: 'https://playwright.dev/',
      },
      Pytest: {
        icon: '/icons/Pytest.svg',
        url: 'https://docs.pytest.org/',
      },
    },
  },
  {
    section: 'Tools',
    tools: {
      Ansible: {
        icon: '/icons/Ansible.svg',
        url: 'https://www.ansible.com/',
      },
      GitHub: {
        icon: '/icons/GitHub.svg',
        url: 'https://www.github.com/',
      },
      Docker: {
        icon: '/icons/Docker.svg',
        url: 'https://www.docker.com/',
      },
    },
  },
]
