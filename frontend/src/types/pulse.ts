export type ActivityEventItem = {
  activityType: string
  githubRepository?: {
    id: string
    key: string
    name: string
    url?: string | null
  } | null
  githubUser?: {
    avatarUrl?: string | null
    id: string
    login: string
    name?: string | null
  } | null
  id: string
  number?: number | null
  occurredAt: string
  title?: string | null
  url?: string | null
}

export type ActivityEventStats = {
  activeRepos?: number
  contributors?: number
  issues?: number
  pullRequests?: number
  releases?: number
  totalActivities?: number
}

export type PulseFiltersProps = {
  activityType: string
  chapterKey: string
  chapterSearchInput: string
  chapterSuggestions: Array<{ id: string; name: string }>
  clearAllFilters: () => void
  handleSelectChapter: (chapter: { id: string; name: string }) => void
  handleSelectProject: (project: { id: string; name: string }) => void
  isSearchingChapters: boolean
  isSearchingProjects: boolean
  order: string
  projectKey: string
  projectSearchInput: string
  projectSuggestions: Array<{ id: string; name: string }>
  searchQuery: string
  setActivityType: (value: string) => void
  setChapterKey: (value: string) => void
  setChapterSearchInput: (value: string) => void
  setOrder: (value: string) => void
  setPage: (page: number) => void
  setProjectKey: (value: string) => void
  setProjectSearchInput: (value: string) => void
  setSearchQuery: (value: string) => void
  setShowChapterSuggestions: (value: boolean) => void
  setShowProjectSuggestions: (value: boolean) => void
  setTimeRange: (value: string) => void
  showChapterSuggestions: boolean
  showProjectSuggestions: boolean
  timeRange: string
}

export type PulseMetricsCardsProps = {
  loading?: boolean
  stats?: ActivityEventStats | null
}

export type PulseTimelineItemProps = {
  event: ActivityEventItem
}
