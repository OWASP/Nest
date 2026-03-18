import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import MembersFilter, { AFFINITY_FILTERS, ROLE_FILTERS } from 'components/MembersFilter'

const defaultProps = {
  selectedAffinity: 'all',
  onAffinityChange: jest.fn(),
  selectedMemberType: 'all',
  onMemberTypeChange: jest.fn(),
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

  it('shows selected member type when provided', () => {
    render(<MembersFilter {...defaultProps} selectedMemberType="staff" />)
    expect(screen.getByRole('button')).toHaveTextContent('OWASP Staff')
  })

  it('calls onAffinityChange when a new affinity is chosen', () => {
    render(<MembersFilter {...defaultProps} />)
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    fireEvent.change(hiddenSelect, { target: { value: 'projects' } })
    expect(defaultProps.onAffinityChange).toHaveBeenCalledWith('projects')
  })

  it('calls onMemberTypeChange when a new member type is chosen', () => {
    render(<MembersFilter {...defaultProps} />)
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    fireEvent.change(hiddenSelect, { target: { value: 'staff' } })
    expect(defaultProps.onMemberTypeChange).toHaveBeenCalledWith('staff')
  })

  it('does not call member type callback when only affinity changes', () => {
    render(<MembersFilter {...defaultProps} />)
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    fireEvent.change(hiddenSelect, { target: { value: 'chapters' } })
    expect(defaultProps.onMemberTypeChange).not.toHaveBeenCalled()
  })

  it('does not call affinity callback when only member type changes', () => {
    render(<MembersFilter {...defaultProps} />)
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    fireEvent.change(hiddenSelect, { target: { value: 'board' } })
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
      expect(screen.getByTestId('type-option-staff')).toBeInTheDocument()
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

  it('ROLE_FILTERS has keys [staff, board, gsoc]', () => {
    expect(ROLE_FILTERS.map((f) => f.key)).toEqual(['staff', 'board', 'gsoc'])
  })

  it('ROLE_FILTERS has labels [OWASP Staff, Board Member, GSoC Mentor]', () => {
    expect(ROLE_FILTERS.map((f) => f.label)).toEqual(['OWASP Staff', 'Board Member', 'GSoC Mentor'])
  })

  it('ROLE_FILTERS facetKeys follow idx_ convention', () => {
    expect(ROLE_FILTERS.map((f) => f.facetKey)).toEqual([
      'idx_is_owasp_staff',
      'idx_owasp_board_member',
      'idx_owasp_gsoc_mentor',
    ])
  })

  it('ROLE_FILTERS all belong to group "role"', () => {
    expect(ROLE_FILTERS.every((f) => f.group === 'role')).toBe(true)
  })
})
