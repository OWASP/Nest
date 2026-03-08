import { groupTimelineByPhase } from 'utils/timelineUtils'

describe('groupTimelineByPhase', () => {
  it('groups consecutive items with the same phase', () => {
    const items = [
      { title: 'A', description: 'desc', phase: 'Maturity & Recognition', year: 'October 2025' },
      { title: 'B', description: 'desc', phase: 'Maturity & Recognition', year: 'November 2025' },
      { title: 'C', description: 'desc', phase: 'Community & Growth', year: 'June 2025' },
    ]
    const groups = groupTimelineByPhase(items)
    expect(groups).toHaveLength(2)
    expect(groups[0].phase).toBe('Maturity & Recognition')
    expect(groups[0].items).toHaveLength(2)
    expect(groups[1].phase).toBe('Community & Growth')
    expect(groups[1].items).toHaveLength(1)
  })

  it('creates separate groups for different phases', () => {
    const items = [
      {
        title: 'A',
        description: 'desc',
        phase: 'Maturity & Recognition',
        year: 'February 2026',
      },
      { title: 'B', description: 'desc', phase: 'Launch', year: 'February 2025' },
      { title: 'C', description: 'desc', phase: 'Foundation', year: 'August 2024' },
    ]
    const groups = groupTimelineByPhase(items)
    expect(groups).toHaveLength(3)
    expect(groups[0].phase).toBe('Maturity & Recognition')
    expect(groups[1].phase).toBe('Launch')
    expect(groups[2].phase).toBe('Foundation')
  })

  it('returns empty array for empty input', () => {
    expect(groupTimelineByPhase([])).toEqual([])
  })

  it('preserves item order within groups', () => {
    const items = [
      { title: 'First', description: 'desc', phase: 'Foundation', year: 'August 2024' },
      { title: 'Second', description: 'desc', phase: 'Foundation', year: 'September 2024' },
      { title: 'Third', description: 'desc', phase: 'Foundation', year: 'November 2024' },
    ]
    const groups = groupTimelineByPhase(items)
    expect(groups).toHaveLength(1)
    expect(groups[0].items[0].title).toBe('First')
    expect(groups[0].items[1].title).toBe('Second')
    expect(groups[0].items[2].title).toBe('Third')
  })

  it('handles single item', () => {
    const items = [
      { title: 'Only', description: 'desc', phase: 'Launch', year: 'February 2025' },
    ]
    const groups = groupTimelineByPhase(items)
    expect(groups).toHaveLength(1)
    expect(groups[0].phase).toBe('Launch')
    expect(groups[0].items).toHaveLength(1)
  })
})
