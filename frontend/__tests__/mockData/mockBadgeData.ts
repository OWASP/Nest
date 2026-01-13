import type { Badge } from 'types/badge'

export const mockBadgeData: Badge[] = [
  {
    id: '1',
    name: 'Contributor',
    cssClass: 'fa-medal',
    description: 'Active contributor to OWASP projects',
    weight: 1,
  },
  {
    id: '2',
    name: 'Security Expert',
    cssClass: 'fa-shield-alt',
    description: 'Security expertise demonstrated',
    weight: 2,
  },
  {
    id: '3',
    name: 'Code Reviewer',
    cssClass: 'fa-code',
    description: 'Regular code reviewer',
    weight: 1,
  },
  {
    id: '4',
    name: 'Mentor',
    cssClass: 'fa-user-graduate',
    description: 'Mentors other contributors',
    weight: 3,
  },
  {
    id: '5',
    name: 'Project Lead',
    cssClass: 'fa-crown',
    description: 'Leads OWASP projects',
    weight: 4,
  },
]

export const mockUserBadgeQueryResponse = {
  user: {
    id: '1',
    login: 'testuser',
    name: 'Test User',
    badges: mockBadgeData,
    badgeCount: 5,
  },
}

export const mockUserWithoutBadgeQueryResponse = {
  user: {
    id: '2',
    login: 'testuser2',
    name: 'Test User 2',
    badges: [],
    badgeCount: 0,
  },
}

export const mockBadgeQueryResponse = {
  badges: mockBadgeData,
}
