import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import MembersFilter, { AFFINITY_FILTERS } from 'components/MembersFilter'

const defaultProps = {
  selectedAffinity: 'all',
  onAffinityChange: jest.fn(),
}

describe('<MembersFilter />', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders the inline filter wrapper and select trigger', () => {
    render(<MembersFilter {...defaultProps} />)
    expect(screen.getByTestId('members-filter')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'All Filters' })).toBeInTheDocument()
  })

  it('shows selected affinity when provided', () => {
    render(<MembersFilter {...defaultProps} selectedAffinity="projects" />)
    expect(screen.getByRole('button')).toHaveTextContent('Projects')
  })

  it('calls onAffinityChange when a new affinity is chosen', () => {
    render(<MembersFilter {...defaultProps} />)
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    fireEvent.change(hiddenSelect, { target: { value: 'projects' } })
    expect(defaultProps.onAffinityChange).toHaveBeenCalledWith('projects')
  })

  it('calls onAffinityChange with "all" when reset is chosen', () => {
    render(<MembersFilter {...defaultProps} selectedAffinity="projects" />)
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    fireEvent.change(hiddenSelect, { target: { value: 'all' } })
    expect(defaultProps.onAffinityChange).toHaveBeenCalledWith('all')
  })

  it('does not call onAffinityChange for unknown option', () => {
    render(<MembersFilter {...defaultProps} />)
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    fireEvent.change(hiddenSelect, { target: { value: 'unknown' } })
    expect(defaultProps.onAffinityChange).not.toHaveBeenCalled()
  })

  it('renders all filter options in the DOM', async () => {
    render(<MembersFilter {...defaultProps} />)
    const trigger = screen.getByRole('button', { name: 'All Filters' })
    fireEvent.click(trigger)
    await waitFor(() => {
      expect(screen.getByTestId('affinity-option-projects')).toBeInTheDocument()
      expect(screen.getByTestId('affinity-option-chapters')).toBeInTheDocument()
      expect(screen.getByTestId('affinity-option-committees')).toBeInTheDocument()
    })
  })

  it('AFFINITY_FILTERS has keys [projects, chapters, committees]', () => {
    expect(AFFINITY_FILTERS.map((f) => f.key)).toEqual(['projects', 'chapters', 'committees'])
  })

  it('AFFINITY_FILTERS has labels [Projects, Chapters, Committees]', () => {
    expect(AFFINITY_FILTERS.map((f) => f.label)).toEqual(['Projects', 'Chapters', 'Committees'])
  })

  it('AFFINITY_FILTERS facetKeys follow idx_ convention', () => {
    expect(AFFINITY_FILTERS.map((f) => f.facetKey)).toEqual([
      'idx_has_project_affinity',
      'idx_has_chapter_affinity',
      'idx_has_committee_affinity',
    ])
  })

  it('AFFINITY_FILTERS all belong to group "affinity"', () => {
    expect(AFFINITY_FILTERS.every((f) => f.group === 'affinity')).toBe(true)
  })
})
