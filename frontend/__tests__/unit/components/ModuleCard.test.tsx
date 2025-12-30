import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { Module } from 'types/mentorship'
import ModuleCard, { getSimpleDuration } from 'components/ModuleCard'

// Mock necessary modules
jest.mock('next/navigation', () => ({
  usePathname: () => '/mentorship/123',
}))
jest.mock('components/SingleModuleCard', () => ({
  __esModule: true,
  default: ({ module }: { module: Module }) => (
    <div data-testid="single-module-card">{module.name}</div>
  ),
}))
jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text: string }) => <span>{text}</span>,
}))

jest.mock('@dnd-kit/core', () => ({
  DndContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DragOverlay: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  closestCorners: jest.fn(),
}))
jest.mock('@dnd-kit/sortable', () => ({
  SortableContext: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  arrayMove: jest.fn((items, oldIndex, newIndex) => {
    const newItems = [...items]
    const [removed] = newItems.splice(oldIndex, 1)
    newItems.splice(newIndex, 0, removed)
    return newItems
  }),
  rectSortingStrategy: jest.fn(),
  useSortable: () => ({
    setNodeRef: jest.fn(),
    transform: null,
    transition: null,
    attributes: {},
    listeners: {},
    isDragging: false,
  }),
}))

const mockModules: Module[] = [
  {
    id: '1',
    key: 'module-1',
    name: 'Module One',
    description: '',
    experienceLevel: ExperienceLevelEnum.Beginner,
    startedAt: '2023-01-01T00:00:00Z',
    endedAt: '2023-01-20T00:00:00Z',
    labels: ['label1'],
    mentors: [],
  },
  {
    id: '2',
    key: 'module-2',
    name: 'Module Two',
    description: '',
    experienceLevel: ExperienceLevelEnum.Intermediate,
    startedAt: '2023-02-01T00:00:00Z',
    endedAt: '2023-02-28T00:00:00Z',
    labels: ['label2'],
    mentors: [],
  },
  {
    id: '3',
    key: 'module-3',
    name: 'Module Three',
    description: '',
    experienceLevel: ExperienceLevelEnum.Advanced,
    startedAt: '2023-03-01T00:00:00Z',
    endedAt: '2023-03-15T00:00:00Z',
    labels: [],
    mentors: [],
  },
  {
    id: '4',
    key: 'module-4',
    name: 'Module Four',
    description: '',
    experienceLevel: ExperienceLevelEnum.Beginner,
    startedAt: '2023-04-01T00:00:00Z',
    endedAt: '2023-04-30T00:00:00Z',
    labels: ['label4'],
    mentors: [],
  },
  {
    id: '5',
    key: 'module-5',
    name: 'Module Five',
    description: '',
    experienceLevel: ExperienceLevelEnum.Expert,
    startedAt: '2023-05-01T00:00:00Z',
    endedAt: '2023-05-10T00:00:00Z',
    labels: ['label5'],
    mentors: [],
  },
]

describe('getSimpleDuration', () => {
  it('returns "N/A" if start or end dates are missing', () => {
    expect(getSimpleDuration('', '')).toBe('N/A')
    expect(getSimpleDuration('2023-01-01', '')).toBe('N/A')
    expect(getSimpleDuration('', '2023-01-01')).toBe('N/A')
  })

  it('returns "Invalid duration" for invalid dates', () => {
    expect(getSimpleDuration('invalid', '2023-01-01')).toBe('Invalid duration')
    expect(getSimpleDuration('2023-01-01', 'invalid')).toBe('Invalid duration')
  })

  it('calculates duration in weeks correctly', () => {
    // 20 days -> 3 weeks (ceil(20/7))
    expect(getSimpleDuration('2023-01-01T00:00:00Z', '2023-01-21T00:00:00Z')).toBe('3 weeks')
    // 7 days -> 1 week (ceil(7/7))
    expect(getSimpleDuration('2023-01-01T00:00:00Z', '2023-01-08T00:00:00Z')).toBe('1 week')
    // 1 day -> 1 week (ceil(1/7))
    expect(getSimpleDuration('2023-01-01T00:00:00Z', '2023-01-02T00:00:00Z')).toBe('1 week')
    // Dates as timestamps (seconds)
    expect(getSimpleDuration(1672531200, 1674259200)).toBe('3 weeks') // Jan 1 2023 to Jan 21 2023
  })
})

describe('ModuleCard', () => {
  it('renders SingleModuleCard if only one module is provided', () => {
    render(<ModuleCard modules={[mockModules[0]]} />)
    expect(screen.getByTestId('single-module-card')).toHaveTextContent('Module One')
  })

  it('renders multiple module cards when more than one module is provided (up to 4 initially)', () => {
    render(<ModuleCard modules={mockModules.slice(0, 3)} />) // 3 modules
    expect(screen.getByText('Module One')).toBeInTheDocument()
    expect(screen.getByText('Module Two')).toBeInTheDocument()
    expect(screen.getByText('Module Three')).toBeInTheDocument()
    expect(screen.queryByText('Show more')).not.toBeInTheDocument()
  })

  it('renders "Show more" button and only first 4 modules if more than 4 modules exist', () => {
    render(<ModuleCard modules={mockModules} />) // 5 modules
    expect(screen.getByText('Module One')).toBeInTheDocument()
    expect(screen.getByText('Module Two')).toBeInTheDocument()
    expect(screen.getByText('Module Three')).toBeInTheDocument()
    expect(screen.getByText('Module Four')).toBeInTheDocument()
    expect(screen.queryByText('Module Five')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Show more/i })).toBeInTheDocument()
  })

  it('shows all modules when "Show more" is clicked, and "Show less" button appears', () => {
    render(<ModuleCard modules={mockModules} />)
    fireEvent.click(screen.getByRole('button', { name: /Show more/i }))

    expect(screen.getByText('Module Five')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Show less/i })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Show more/i })).not.toBeInTheDocument()
  })

  it('hides extra modules when "Show less" is clicked', () => {
    render(<ModuleCard modules={mockModules} />)
    fireEvent.click(screen.getByRole('button', { name: /Show more/i }))
    fireEvent.click(screen.getByRole('button', { name: /Show less/i }))

    expect(screen.queryByText('Module Five')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Show more/i })).toBeInTheDocument()
  })

  it('shows "Customize order" button for admin', () => {
    render(<ModuleCard modules={mockModules} accessLevel="admin" />)
    expect(screen.getByRole('button', { name: /Customize order/i })).toBeInTheDocument()
  })

  it('does not show "Customize order" button for non-admin', () => {
    render(<ModuleCard modules={mockModules} accessLevel="user" />)
    expect(screen.queryByRole('button', { name: /Customize order/i })).not.toBeInTheDocument()
  })

  it('switches to reordering mode when "Customize order" is clicked', () => {
    render(<ModuleCard modules={mockModules} accessLevel="admin" />)
    fireEvent.click(screen.getByRole('button', { name: /Customize order/i }))

    expect(screen.getByRole('button', { name: /Save order/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Customize order/i })).not.toBeInTheDocument()
  })

  it('switches out of reordering mode when "Cancel" is clicked', () => {
    render(<ModuleCard modules={mockModules} accessLevel="admin" />)
    fireEvent.click(screen.getByRole('button', { name: /Customize order/i }))
    fireEvent.click(screen.getByRole('button', { name: /Cancel/i }))

    expect(screen.getByRole('button', { name: /Customize order/i })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Save order/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Cancel/i })).not.toBeInTheDocument()
  })

  it('calls setModuleOrder and exits reordering mode when "Save order" is clicked', () => {
    const setModuleOrder = jest.fn()
    render(<ModuleCard modules={mockModules} accessLevel="admin" setModuleOrder={setModuleOrder} />)
    fireEvent.click(screen.getByRole('button', { name: /Customize order/i }))
    fireEvent.click(screen.getByRole('button', { name: /Save order/i }))

    expect(setModuleOrder).toHaveBeenCalledWith(mockModules)
    expect(screen.getByRole('button', { name: /Customize order/i })).toBeInTheDocument()
  })
})
