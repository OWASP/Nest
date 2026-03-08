import type { ProjectTimeline } from 'types/about'

export type TimelineGroup = {
  items: ProjectTimeline[]
  phase: string
}

export function groupTimelineByPhase(items: ProjectTimeline[]): TimelineGroup[] {
  const groups: TimelineGroup[] = []

  for (const item of items) {
    const lastGroup = groups[groups.length - 1]

    if (lastGroup && lastGroup.phase === item.phase) {
      lastGroup.items.push(item)
    } else {
      groups.push({ phase: item.phase, items: [item] })
    }
  }

  return groups
}
