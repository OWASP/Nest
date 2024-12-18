export interface ContributeDataType {
  projects: ProjectDataType
  issues: IssuesDataType
  chapters: ChapterDataType
  committees: CommitteeDataType
}

export const contributeMockData: ContributeDataType = {
  projects: {
    active_projects_count: 2,
    projects: [
      {
        idx_top_contributors: [
          { avatar_url: 'url1', contributions_count: 10, login: 'user1', name: 'User One' },
          { avatar_url: 'url2', contributions_count: 5, login: 'user2', name: 'User Two' },
        ],
        idx_contributors_count: 20,
        idx_forks_count: 15,
        idx_leaders: ['Leader1'],
        idx_level: 'Intermediate',
        idx_name: 'Project One',
        idx_stars_count: 100,
        idx_summary: 'A great open-source project',
        idx_topics: ['React', 'TypeScript'],
        idx_type: 'Open Source',
        idx_updated_at: 1700000000,
        idx_url: 'https://project-one-url.com',
        objectID: '1',
      },
    ],
  },
  issues: {
    issues: [
      {
        idx_comments_count: 3,
        idx_created_at: 1700000000,
        idx_hint: 'Beginner-friendly issue',
        idx_labels: ['good first issue', 'bug'],
        idx_project_name: 'Project One',
        idx_project_url: 'https://project-one-url.com',
        idx_repository_languages: ['JavaScript', 'TypeScript'],
        idx_summary: 'Fix the alignment issue on the homepage',
        idx_title: 'Alignment issue',
        idx_updated_at: 1700000500,
        idx_url: 'https://issue-url.com',
        objectID: 'issue1',
      },
    ],
  },
  chapters: {
    active_chapters_count: 1,
    chapters: [
      {
        idx_created_at: 1700000000,
        idx_leaders: ['Leader1'],
        idx_name: 'Chapter One',
        idx_related_urls: ['https://chapter-one.com'],
        idx_top_contributors: [
          { avatar_url: 'url1', contributions_count: 15, login: 'user1', name: 'User One' },
        ],
        idx_summary: 'A chapter for learning advanced TypeScript.',
        idx_updated_at: 1700000500,
        idx_url: 'https://chapter-one.com',
        objectID: 'chapter1',
      },
    ],
  },
  committees: {
    active_committees_count: 1,
    committees: [
      {
        idx_created_at: 1700000000,
        idx_leaders: ['Leader1'],
        idx_name: 'Committee One',
        idx_related_urls: ['https://committee-one.com'],
        idx_top_contributors: [
          { avatar_url: 'url1', contributions_count: 10, login: 'user1', name: 'User One' },
        ],
        idx_summary: 'A committee for improving documentation',
        idx_updated_at: 1700000500,
        idx_url: 'https://committee-one.com',
        objectID: 'committee1',
      },
    ],
  },
}

export interface ProjectDataType {
  active_projects_count: number
  projects: project[]
}

export type project = {
  idx_top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  idx_contributors_count: number
  idx_forks_count: number
  idx_leaders: string[]
  idx_level: string
  idx_name: string
  idx_stars_count: number
  idx_summary: string
  idx_topics: string[]
  idx_type: string
  idx_updated_at: number // UNIX timestamp
  idx_url: string
  objectID: string
}

export interface IssuesDataType {
  issues: IssueType[]
}

export interface IssueType {
  idx_comments_count: number
  idx_created_at: number
  idx_hint: string
  idx_labels: string[]
  idx_project_name: string
  idx_project_url: string
  idx_repository_languages: string[]
  idx_summary: string
  idx_title: string
  idx_updated_at: number
  idx_url: string
  objectID: string
}

export interface ChapterDataType {
  active_chapters_count: number
  chapters: {
    idx_created_at: number
    idx_leaders: string[]
    idx_name: string
    idx_related_urls: string[]
    idx_top_contributors: {
      avatar_url: string
      contributions_count: number
      login: string
      name: string
    }[]
    idx_summary: string
    idx_updated_at: number
    idx_url: string
    objectID: string
  }[]
}

export interface CommitteeType {
  idx_created_at: number
  idx_leaders: string[]
  idx_name: string
  idx_related_urls: string[]
  idx_top_contributors: {
    avatar_url: string
    contributions_count: number
    login: string
    name: string
  }[]
  idx_summary: string
  idx_updated_at: number
  idx_url: string
  objectID: string
}

export interface CommitteeDataType {
  active_committees_count: number
  committees: CommitteeType[]
}
