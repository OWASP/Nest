export const DEADLINE_ALL = 'all'

export const DEADLINE_OPTIONS = [
  { key: 'all', label: 'All' },
  { key: 'overdue', label: 'Overdue' },
  { key: 'due-soon', label: 'Due Soon' },
  { key: 'upcoming', label: 'Upcoming' },
  { key: 'no-deadline', label: 'No Deadline' },
]

export const getDeadlineCategory = (deadline?: string | null): string => {
  if (!deadline) return 'no-deadline'

  const now = new Date()
  const deadlineDate = new Date(deadline)
  const nowStartUtc = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
  const deadlineStartUtc = Date.UTC(
    deadlineDate.getUTCFullYear(),
    deadlineDate.getUTCMonth(),
    deadlineDate.getUTCDate()
  )
  const diffDays = Math.floor((deadlineStartUtc - nowStartUtc) / 86400000)

  if (diffDays < 0) return 'overdue'
  if (diffDays <= 7) return 'due-soon'
  return 'upcoming'
}
