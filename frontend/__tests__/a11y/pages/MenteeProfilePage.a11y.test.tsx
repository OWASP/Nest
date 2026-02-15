import { useQuery } from '@apollo/client/react'
import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import React from 'react'
import MenteeProfilePage from 'app/my/mentorship/programs/[programKey]/modules/[moduleKey]/mentees/[menteeKey]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useParams: jest.fn(() => ({
    programKey: 'prog1',
    moduleKey: 'mod1',
    menteeKey: 'test-mentee',
  })),
  useRouter: jest.fn(),
}))

// Mock components
jest.mock('components/LabelList', () => ({
  LabelList: ({ labels }: { labels: string[] }) => (
    <div data-testid="label-list">{labels.join(', ')}</div>
  ),
}))

jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: Record<string, unknown>) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={(props.alt as string) || ''} />
  },
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    isDisabled,
  }: {
    children: React.ReactNode
    content: string
    isDisabled?: boolean
  }) => {
    if (isDisabled) {
      return <>{children}</>
    }
    return (
      <div data-testid="tooltip" data-content={content}>
        {children}
      </div>
    )
  },
}))

jest.mock('@heroui/select', () => {
  return {
    Select: ({
      children,
      selectedKeys,
      onSelectionChange,
      'aria-label': ariaLabel,
      classNames: _classNames,
      size: _size,
      ...props
    }: {
      children: React.ReactNode
      selectedKeys: Set<string>
      onSelectionChange?: (keys: Set<string>) => void
      'aria-label'?: string
      classNames?: Record<string, string>
      size?: string
    }) => {
      const [isOpen, setIsOpen] = React.useState(false)
      const selectedKey = Array.from(selectedKeys)[0] || 'all'

      const handleItemClick = (key: string) => {
        if (onSelectionChange) {
          onSelectionChange(new Set([key]))
        }
        setIsOpen(false)
      }

      return (
        <div data-testid="select-wrapper" {...props}>
          <button
            type="button"
            aria-label={ariaLabel}
            aria-expanded={isOpen}
            aria-controls="select-popover"
            onClick={() => setIsOpen(!isOpen)}
            data-testid="select-trigger"
          >
            {selectedKey}
          </button>
          {isOpen && (
            <div id="select-popover" data-testid="select-popover" aria-label="Options">
              {React.Children.map(children, (child: React.ReactElement) => {
                const itemKey = String(child.key ?? '')
                return React.cloneElement(child, {
                  'data-key': itemKey,
                  onClick: () => handleItemClick(itemKey),
                } as Partial<unknown>)
              })}
            </div>
          )}
        </div>
      )
    },
    SelectItem: ({
      children,
      onClick,
      'data-key': dataKey,
      classNames: _classNames,
      ...props
    }: {
      children: React.ReactNode
      onClick?: () => void
      'data-key'?: string
      classNames?: Record<string, string>
    }) => (
      <button
        type="button"
        data-testid="select-item"
        data-key={dataKey}
        onClick={onClick}
        {...props}
      >
        {children}
      </button>
    ),
  }
})

const mockMenteeData = {
  getMenteeDetails: {
    id: 'mentee1',
    login: 'test-mentee',
    name: 'Test Mentee',
    avatarUrl: 'http://example.com/avatar.png',
    bio: 'A test bio.',
    domains: ['frontend', 'backend'],
    tags: ['react', 'nodejs'],
  },
  getMenteeModuleIssues: [
    {
      id: 'issue1',
      number: 101,
      title: 'Open Issue 1',
      state: 'open',
      url: 'http://example.com/issue1',
      labels: ['bug'],
    },
    {
      id: 'issue2',
      number: 102,
      title: 'Closed Issue 1',
      state: 'closed',
      url: 'http://example.com/issue2',
      labels: ['feature'],
    },
    {
      id: 'issue3',
      number: 103,
      title: 'Open Issue 2',
      state: 'open',
      url: 'http://example.com/issue3',
      labels: ['docs'],
    },
  ],
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('MenteeProfilePage Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  afterAll(() => {
    jest.clearAllMocks()
  })

  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockMenteeData,
      loading: false,
      error: null,
    })

    const { container } = render(<MenteeProfilePage />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
