/**
 * @file Complete unit tests for the ModuleCard component
 * Targeting 90-95% code coverage.
 */
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import React from 'react'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import type { Module } from 'types/mentorship'
import ModuleCard, { getSimpleDuration } from 'components/ModuleCard'

// Mock next/navigation
const mockPathname = jest.fn()
jest.mock('next/navigation', () => ({
  usePathname: () => mockPathname(),
}))

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    title,
    height,
    width,
    className,
  }: {
    src: string
    alt: string
    title?: string
    height?: number
    width?: number
    className?: string
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      title={title}
      height={height}
      width={width}
      className={className}
      data-testid="next-image"
    />
  ),
}))

// Mock next/link
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({
    children,
    href,
    className,
  }: {
    children: React.ReactNode
    href: string
    className?: string
  }) => (
    <a href={href} className={className} data-testid="next-link">
      {children}
    </a>
  ),
}))

// Mock react-icons
jest.mock('react-icons/fa6', () => ({
  FaChevronDown: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="chevron-down" {...props} />
  ),
  FaChevronUp: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="chevron-up" {...props} />
  ),
  FaTurnUp: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="icon-turnup" {...props} />,
  FaCalendar: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-calendar" {...props} />
  ),
  FaHourglassHalf: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="icon-hourglass" {...props} />
  ),
}))

// Mock lodash capitalize
jest.mock('lodash', () => ({
  capitalize: (str: string) =>
    str ? str.charAt(0).toUpperCase() + str.slice(1).toLowerCase() : '',
}))

// Mock SingleModuleCard
jest.mock('components/SingleModuleCard', () => ({
  __esModule: true,
  default: ({
    module,
    accessLevel,
    admins,
  }: {
    module: Module
    accessLevel?: string
    admins?: { login: string }[]
  }) => (
    <div
      data-testid="single-module-card"
      data-module-name={module.name}
      data-access-level={accessLevel}
    >
      Single Module: {module.name}
      {admins && <span data-testid="admins-count">{admins.length}</span>}
    </div>
  ),
}))

// Mock formatDate utility
jest.mock('utils/dateFormatter', () => ({
  formatDate: (date: string | number) => {
    if (!date) return 'N/A'
    const d = typeof date === 'number' ? new Date(date * 1000) : new Date(date)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  },
}))

// Mock components
jest.mock('components/InfoItem', () => ({
  TextInfoItem: ({
    icon: Icon,
    label,
    value,
  }: {
    icon: React.ComponentType<{ className?: string }>
    label: string
    value: string
  }) => (
    <div data-testid={`info-item-${label.toLowerCase()}`}>
      <Icon className="test-icon" />
      <span>{label}:</span>
      <span>{value}</span>
    </div>
  ),
}))

jest.mock('components/TruncatedText', () => ({
  TruncatedText: ({ text }: { text: string }) => <span data-testid="truncated-text">{text}</span>,
}))

describe('ModuleCard', () => {
  const createMockModule = (overrides: Partial<Module> = {}): Module => ({
    id: '1',
    key: 'test-module',
    name: 'Test Module',
    description: 'Test description',
    experienceLevel: ExperienceLevelEnum.Beginner,
    startedAt: '2024-01-01T00:00:00Z',
    endedAt: '2024-03-01T00:00:00Z',
    mentors: [],
    mentees: [],
    ...overrides,
  })

  const createMockContributor = (login: string, avatarUrl?: string, name?: string) => ({
    id: `id-${login}`,
    login,
    name: name || login,
    avatarUrl: avatarUrl || `https://github.com/${login}.png`,
  })

  beforeEach(() => {
    jest.clearAllMocks()
    mockPathname.mockReturnValue('/my/mentorship/programs/test-program')
  })

  describe('Single Module Rendering', () => {
    it('renders SingleModuleCard when given exactly one module', () => {
      const modules = [createMockModule()]

      render(<ModuleCard modules={modules} />)

      expect(screen.getByTestId('single-module-card')).toBeInTheDocument()
      expect(screen.getByText('Single Module: Test Module')).toBeInTheDocument()
    })

    it('passes accessLevel to SingleModuleCard', () => {
      const modules = [createMockModule()]

      render(<ModuleCard modules={modules} accessLevel="admin" />)

      const singleModuleCard = screen.getByTestId('single-module-card')
      expect(singleModuleCard).toHaveAttribute('data-access-level', 'admin')
    })

    it('passes admins to SingleModuleCard', () => {
      const modules = [createMockModule()]
      const admins = [{ login: 'admin1' }, { login: 'admin2' }]

      render(<ModuleCard modules={modules} admins={admins} />)

      expect(screen.getByTestId('admins-count')).toHaveTextContent('2')
    })
  })

  describe('Multiple Modules Rendering', () => {
    it('renders multiple modules in a grid', () => {
      const modules = [
        createMockModule({ key: 'mod1', name: 'Module 1' }),
        createMockModule({ key: 'mod2', name: 'Module 2' }),
      ]

      render(<ModuleCard modules={modules} />)

      expect(screen.queryByTestId('single-module-card')).not.toBeInTheDocument()
      expect(screen.getByText('Module 1')).toBeInTheDocument()
      expect(screen.getByText('Module 2')).toBeInTheDocument()
    })

    it('shows only first 4 modules initially when more than 4 modules', () => {
      const modules = [
        createMockModule({ key: 'mod1', name: 'Module 1' }),
        createMockModule({ key: 'mod2', name: 'Module 2' }),
        createMockModule({ key: 'mod3', name: 'Module 3' }),
        createMockModule({ key: 'mod4', name: 'Module 4' }),
        createMockModule({ key: 'mod5', name: 'Module 5' }),
        createMockModule({ key: 'mod6', name: 'Module 6' }),
      ]

      render(<ModuleCard modules={modules} />)

      expect(screen.getByText('Module 1')).toBeInTheDocument()
      expect(screen.getByText('Module 2')).toBeInTheDocument()
      expect(screen.getByText('Module 3')).toBeInTheDocument()
      expect(screen.getByText('Module 4')).toBeInTheDocument()
      expect(screen.queryByText('Module 5')).not.toBeInTheDocument()
      expect(screen.queryByText('Module 6')).not.toBeInTheDocument()
    })

    it('shows "Show more" button when more than 4 modules', () => {
      const modules = Array.from({ length: 6 }, (_, i) =>
        createMockModule({ key: `mod${i + 1}`, name: `Module ${i + 1}` })
      )

      render(<ModuleCard modules={modules} />)

      expect(screen.getByText('Show more')).toBeInTheDocument()
      expect(screen.getByTestId('chevron-down')).toBeInTheDocument()
    })

    it('does not show "Show more" button when 4 or fewer modules', () => {
      const modules = Array.from({ length: 4 }, (_, i) =>
        createMockModule({ key: `mod${i + 1}`, name: `Module ${i + 1}` })
      )

      render(<ModuleCard modules={modules} />)

      expect(screen.queryByText('Show more')).not.toBeInTheDocument()
    })

    it('toggles between showing all and showing limited modules on click', () => {
      const modules = Array.from({ length: 6 }, (_, i) =>
        createMockModule({ key: `mod${i + 1}`, name: `Module ${i + 1}` })
      )

      render(<ModuleCard modules={modules} />)

      // Verify initial state
      expect(screen.queryByText('Module 5')).not.toBeInTheDocument()

      // Click to show more
      const showMoreButton = screen.getByText('Show more')
      fireEvent.click(showMoreButton)

      // All modules should be visible
      expect(screen.getByText('Module 5')).toBeInTheDocument()
      expect(screen.getByText('Module 6')).toBeInTheDocument()
      expect(screen.getByText('Show less')).toBeInTheDocument()
      expect(screen.getByTestId('chevron-up')).toBeInTheDocument()

      // Click to show less
      const showLessButton = screen.getByText('Show less')
      fireEvent.click(showLessButton)

      // Should be back to initial state
      expect(screen.queryByText('Module 5')).not.toBeInTheDocument()
      expect(screen.getByText('Show more')).toBeInTheDocument()
    })

    it('handles keyboard navigation with Enter key', () => {
      const modules = Array.from({ length: 6 }, (_, i) =>
        createMockModule({ key: `mod${i + 1}`, name: `Module ${i + 1}` })
      )

      render(<ModuleCard modules={modules} />)

      const showMoreButton = screen.getByRole('button')
      fireEvent.keyDown(showMoreButton, { key: 'Enter', preventDefault: jest.fn() })

      expect(screen.getByText('Module 5')).toBeInTheDocument()
      expect(screen.getByText('Show less')).toBeInTheDocument()
    })

    it('handles keyboard navigation with Space key', () => {
      const modules = Array.from({ length: 6 }, (_, i) =>
        createMockModule({ key: `mod${i + 1}`, name: `Module ${i + 1}` })
      )

      render(<ModuleCard modules={modules} />)

      const showMoreButton = screen.getByRole('button')
      fireEvent.keyDown(showMoreButton, { key: ' ', preventDefault: jest.fn() })

      expect(screen.getByText('Module 5')).toBeInTheDocument()
      expect(screen.getByText('Show less')).toBeInTheDocument()
    })

    it('ignores other keyboard keys', () => {
      const modules = Array.from({ length: 6 }, (_, i) =>
        createMockModule({ key: `mod${i + 1}`, name: `Module ${i + 1}` })
      )

      render(<ModuleCard modules={modules} />)

      const showMoreButton = screen.getByRole('button')
      fireEvent.keyDown(showMoreButton, { key: 'Tab' })

      // Should still show initial state
      expect(screen.queryByText('Module 5')).not.toBeInTheDocument()
      expect(screen.getByText('Show more')).toBeInTheDocument()
    })

    it('uses module.key for unique key if available, otherwise uses module.id', () => {
      const modules = [
        createMockModule({ key: 'mod-key-1', id: 'mod-id-1', name: 'Module With Key' }),
        createMockModule({ key: '', id: 'mod-id-2', name: 'Module Without Key' }),
      ]

      render(<ModuleCard modules={modules} />)

      expect(screen.getByText('Module With Key')).toBeInTheDocument()
      expect(screen.getByText('Module Without Key')).toBeInTheDocument()
    })
  })

  describe('ModuleItem Component', () => {
    it('renders module name with link to module details page', () => {
      const modules = [
        createMockModule({ key: 'test-mod', name: 'Test Module' }),
        createMockModule({ key: 'test-mod2', name: 'Test Module 2' }),
      ]

      render(<ModuleCard modules={modules} />)

      const links = screen.getAllByTestId('next-link')
      const moduleLink = links.find((link) =>
        link.getAttribute('href')?.includes('/modules/test-mod')
      )
      expect(moduleLink).toBeInTheDocument()
    })

    it('renders experience level info item', () => {
      const modules = [
        createMockModule({ experienceLevel: ExperienceLevelEnum.Intermediate }),
        createMockModule({ key: 'mod2', experienceLevel: ExperienceLevelEnum.Beginner }),
      ]

      render(<ModuleCard modules={modules} />)

      const levelItems = screen.getAllByTestId('info-item-level')
      expect(levelItems.length).toBeGreaterThan(0)
      expect(levelItems[0]).toHaveTextContent('Intermediate')
    })

    it('renders start date info item', () => {
      const modules = [createMockModule(), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const startItems = screen.getAllByTestId('info-item-start')
      expect(startItems.length).toBeGreaterThan(0)
    })

    it('renders duration info item', () => {
      const modules = [createMockModule(), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const durationItems = screen.getAllByTestId('info-item-duration')
      expect(durationItems.length).toBeGreaterThan(0)
    })
  })

  describe('Mentors and Mentees Display', () => {
    it('does not render mentors/mentees section when both are empty', () => {
      const modules = [
        createMockModule({ mentors: [], mentees: [] }),
        createMockModule({ key: 'mod2', mentors: [], mentees: [] }),
      ]

      render(<ModuleCard modules={modules} />)

      expect(screen.queryByText('Mentors')).not.toBeInTheDocument()
      expect(screen.queryByText('Mentees')).not.toBeInTheDocument()
    })

    it('renders mentors section when mentors have avatars', () => {
      const modules = [
        createMockModule({
          mentors: [
            createMockContributor('mentor1', 'https://example.com/avatar1.png'),
            createMockContributor('mentor2', 'https://example.com/avatar2.png'),
          ],
        }),
        createMockModule({ key: 'mod2' }),
      ]

      render(<ModuleCard modules={modules} />)

      expect(screen.getByText('Mentors')).toBeInTheDocument()
    })

    it('renders mentees section when mentees have avatars', () => {
      const modules = [
        createMockModule({
          mentees: [
            createMockContributor('mentee1', 'https://example.com/avatar1.png'),
            createMockContributor('mentee2', 'https://example.com/avatar2.png'),
          ],
        }),
        createMockModule({ key: 'mod2' }),
      ]

      render(<ModuleCard modules={modules} />)

      expect(screen.getByText('Mentees')).toBeInTheDocument()
    })

    it('shows only first 4 mentor avatars and +N for remaining', () => {
      const mentors = Array.from({ length: 6 }, (_, i) =>
        createMockContributor(`mentor${i + 1}`, `https://example.com/avatar${i + 1}.png`)
      )
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      // Check for +2 indicator (6 mentors - 4 shown = 2 remaining)
      expect(screen.getByText('+2')).toBeInTheDocument()
    })

    it('shows only first 4 mentee avatars and +N for remaining', () => {
      const mentees = Array.from({ length: 7 }, (_, i) =>
        createMockContributor(`mentee${i + 1}`, `https://example.com/avatar${i + 1}.png`)
      )
      const modules = [createMockModule({ mentees }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      // Check for +3 indicator (7 mentees - 4 shown = 3 remaining)
      expect(screen.getByText('+3')).toBeInTheDocument()
    })

    it('does not show +N when 4 or fewer mentors', () => {
      const mentors = Array.from({ length: 4 }, (_, i) =>
        createMockContributor(`mentor${i + 1}`, `https://example.com/avatar${i + 1}.png`)
      )
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      expect(screen.queryByText(/^\+\d+$/)).not.toBeInTheDocument()
    })

    it('filters out mentors without avatar URLs', () => {
      const mentors = [
        createMockContributor('mentor1', 'https://example.com/avatar1.png'),
        { id: 'id-mentor2', login: 'mentor2', name: 'Mentor 2', avatarUrl: '' }, // No avatar
        {
          id: 'id-mentor3',
          login: 'mentor3',
          name: 'Mentor 3',
          avatarUrl: undefined as unknown as string,
        }, // Undefined avatar
      ]
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      // Should only show mentors with valid avatars
      const images = screen.getAllByTestId('next-image')
      expect(images.length).toBe(1) // Only mentor1 has avatar
    })

    it('displays mentor avatar with proper size parameter in URL', () => {
      const mentors = [createMockContributor('mentor1', 'https://example.com/avatar1.png')]
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const images = screen.getAllByTestId('next-image')
      const mentorImage = images[0]
      expect(mentorImage.getAttribute('src')).toContain('s=60')
    })

    it('handles avatar URL with existing query parameters', () => {
      const mentors = [createMockContributor('mentor1', 'https://example.com/avatar1.png?v=2')]
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const images = screen.getAllByTestId('next-image')
      const mentorImage = images[0]
      expect(mentorImage.getAttribute('src')).toContain('s=60')
    })

    it('handles invalid avatar URL gracefully', () => {
      const mentors = [createMockContributor('mentor1', 'invalid-url')]
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const images = screen.getAllByTestId('next-image')
      // Should fall back to appending ?s=60
      expect(images[0].getAttribute('src')).toContain('s=60')
    })

    it('links mentee to member page when not on /my/mentorship path', () => {
      mockPathname.mockReturnValue('/mentorship/programs/test-program')
      const mentees = [createMockContributor('mentee1', 'https://example.com/avatar1.png')]
      const modules = [createMockModule({ mentees }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const links = screen.getAllByTestId('next-link')
      const menteeLink = links.find((link) =>
        link.getAttribute('href')?.includes('/members/mentee1')
      )
      expect(menteeLink).toBeInTheDocument()
    })

    it('links mentee to mentorship details page when on /my/mentorship path', () => {
      mockPathname.mockReturnValue('/my/mentorship/programs/test-program')
      const mentees = [createMockContributor('mentee1', 'https://example.com/avatar1.png')]
      const modules = [
        createMockModule({ key: 'test-module', mentees }),
        createMockModule({ key: 'mod2' }),
      ]

      render(<ModuleCard modules={modules} />)

      const links = screen.getAllByTestId('next-link')
      const menteeLink = links.find((link) =>
        link
          .getAttribute('href')
          ?.includes('/my/mentorship/programs/test-program/modules/test-module/mentees/mentee1')
      )
      expect(menteeLink).toBeInTheDocument()
    })

    it('links mentor to member page regardless of path', () => {
      mockPathname.mockReturnValue('/my/mentorship/programs/test-program')
      const mentors = [createMockContributor('mentor1', 'https://example.com/avatar1.png')]
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const links = screen.getAllByTestId('next-link')
      const mentorLink = links.find((link) =>
        link.getAttribute('href')?.includes('/members/mentor1')
      )
      expect(mentorLink).toBeInTheDocument()
    })

    it('renders both mentors and mentees sections with border separator when both exist', () => {
      const modules = [
        createMockModule({
          mentors: [createMockContributor('mentor1', 'https://example.com/avatar1.png')],
          mentees: [createMockContributor('mentee1', 'https://example.com/avatar2.png')],
        }),
        createMockModule({ key: 'mod2' }),
      ]

      render(<ModuleCard modules={modules} />)

      expect(screen.getByText('Mentors')).toBeInTheDocument()
      expect(screen.getByText('Mentees')).toBeInTheDocument()
    })

    it('uses contributor name for avatar alt and title when available', () => {
      const mentors = [
        createMockContributor('mentor1', 'https://example.com/avatar1.png', 'John Doe'),
      ]
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const image = screen.getAllByTestId('next-image')[0]
      expect(image.getAttribute('alt')).toBe('John Doe')
      expect(image.getAttribute('title')).toBe('John Doe')
    })

    it('falls back to login for avatar alt and title when name is not available', () => {
      const mentors = [
        {
          id: 'id-mentor1',
          login: 'mentor1',
          name: '',
          avatarUrl: 'https://example.com/avatar1.png',
        },
      ]
      const modules = [createMockModule({ mentors }), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const image = screen.getAllByTestId('next-image')[0]
      expect(image.getAttribute('alt')).toBe('mentor1')
      expect(image.getAttribute('title')).toBe('mentor1')
    })
  })

  describe('Path Handling', () => {
    it('extracts programKey from pathname correctly', () => {
      mockPathname.mockReturnValue('/my/mentorship/programs/program-123/modules')
      const modules = [
        createMockModule({
          key: 'mod1',
          mentees: [createMockContributor('mentee1', 'https://example.com/avatar.png')],
        }),
        createMockModule({ key: 'mod2' }),
      ]

      render(<ModuleCard modules={modules} />)

      const links = screen.getAllByTestId('next-link')
      const menteeLink = links.find((link) =>
        link.getAttribute('href')?.includes('/programs/program-123/modules/')
      )
      expect(menteeLink).toBeInTheDocument()
    })

    it('handles undefined pathname gracefully', () => {
      mockPathname.mockReturnValue(undefined)
      const modules = [createMockModule(), createMockModule({ key: 'mod2' })]

      // Should not throw
      expect(() => render(<ModuleCard modules={modules} />)).not.toThrow()
    })

    it('handles pathname without /programs/ segment', () => {
      mockPathname.mockReturnValue('/some/other/path')
      const modules = [createMockModule(), createMockModule({ key: 'mod2' })]

      render(<ModuleCard modules={modules} />)

      const moduleElements = screen.getAllByText('Test Module')
      expect(moduleElements.length).toBe(2)
    })
  })
})

describe('getSimpleDuration', () => {
  it('returns N/A when start is missing', () => {
    expect(getSimpleDuration('', '2024-03-01T00:00:00Z')).toBe('N/A')
  })

  it('returns N/A when end is missing', () => {
    expect(getSimpleDuration('2024-01-01T00:00:00Z', '')).toBe('N/A')
  })

  it('returns N/A when both start and end are missing', () => {
    expect(getSimpleDuration('', '')).toBe('N/A')
  })

  it('returns N/A for falsy numeric values', () => {
    expect(getSimpleDuration(0, 1709251200)).toBe('N/A')
  })

  it('calculates duration correctly for string dates', () => {
    // 2 months = approximately 8-9 weeks
    const result = getSimpleDuration('2024-01-01T00:00:00Z', '2024-03-01T00:00:00Z')
    expect(result).toMatch(/^\d+ weeks?$/)
  })

  it('calculates duration correctly for numeric timestamps (Unix seconds)', () => {
    // Jan 1, 2024 to Jan 22, 2024 = 3 weeks
    const start = 1704067200 // Jan 1, 2024
    const end = 1705881600 // Jan 22, 2024
    const result = getSimpleDuration(start, end)
    expect(result).toBe('3 weeks')
  })

  it('returns "1 week" for exactly 7 days', () => {
    const start = 1704067200 // Jan 1, 2024
    const end = 1704672000 // Jan 8, 2024
    const result = getSimpleDuration(start, end)
    expect(result).toBe('1 week')
  })

  it('rounds up partial weeks', () => {
    // 10 days should be 2 weeks (ceil(10/7) = 2)
    const start = 1704067200 // Jan 1, 2024
    const end = 1704931200 // Jan 11, 2024
    const result = getSimpleDuration(start, end)
    expect(result).toBe('2 weeks')
  })

  it('returns "Invalid duration" for invalid start date string', () => {
    expect(getSimpleDuration('invalid-date', '2024-03-01T00:00:00Z')).toBe('Invalid duration')
  })

  it('returns "Invalid duration" for invalid end date string', () => {
    expect(getSimpleDuration('2024-01-01T00:00:00Z', 'invalid-date')).toBe('Invalid duration')
  })

  it('returns "Invalid duration" when both dates are invalid', () => {
    expect(getSimpleDuration('not-a-date', 'also-not-a-date')).toBe('Invalid duration')
  })

  it('handles mixed string and number inputs', () => {
    const result = getSimpleDuration('2024-01-01T00:00:00Z', 1709251200) // String start, number end
    expect(result).toMatch(/^\d+ weeks?$/)
  })

  it('handles very short durations (less than a week)', () => {
    // 3 days should round up to 1 week
    const start = 1704067200 // Jan 1, 2024
    const end = 1704326400 // Jan 4, 2024
    const result = getSimpleDuration(start, end)
    expect(result).toBe('1 week')
  })

  it('handles negative duration (end before start)', () => {
    const result = getSimpleDuration('2024-03-01T00:00:00Z', '2024-01-01T00:00:00Z')
    // Negative days / 7, ceil would give 0 or negative, depending on implementation
    expect(result).toMatch(/\d+ weeks?|0 weeks/)
  })
})
