import { screen, render, fireEvent } from '@testing-library/react'
import { ReactNode } from 'react'
import type { CardProps } from 'types/card'
import Card from 'components/Card'

// Define proper types for mock props
interface MockLinkProps {
  children: ReactNode
  href: string
  target?: string
  rel?: string
  className?: string
}

interface MockFontAwesomeIconProps {
  icon: unknown
  className?: string
}

interface MockTooltipProps {
  children: ReactNode
  content: string
  id?: string
  placement?: string
}

interface MockActionButtonProps {
  children: ReactNode
  onClick?: () => void
  tooltipLabel?: string
  url?: string
}

interface MockContributorAvatarProps {
  contributor: {
    login?: string
    name?: string
    avatarUrl?: string
  }
  uniqueKey: string
}

interface MockDisplayIconProps {
  item: string
  icons?: Record<string, unknown>
}

interface MockMarkdownProps {
  content: string
  className?: string
}

jest.mock('next/link', () => {
  return function MockedLink({ children, href, ...props }: MockLinkProps) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon, className }: MockFontAwesomeIconProps) => (
    <span data-testid="font-awesome-icon" className={className}>
      {String(icon)}
    </span>
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content, id }: MockTooltipProps) => (
    <div data-testid="tooltip" title={content} id={id}>
      {children}
    </div>
  ),
}))

jest.mock('wrappers/FontAwesomeIconWrapper', () => {
  return function FontAwesomeIconWrapper({ icon, className }: MockFontAwesomeIconProps) {
    return (
      <span data-testid="font-awesome-wrapper" className={className}>
        {String(icon)}
      </span>
    )
  }
})

jest.mock('components/ActionButton', () => {
  return function ActionButton({ children, onClick, tooltipLabel, url }: MockActionButtonProps) {
    return (
      <button data-testid="action-button" onClick={onClick} data-url={url} title={tooltipLabel}>
        {children}
      </button>
    )
  }
})

jest.mock('components/ContributorAvatar', () => {
  return function ContributorAvatar({ contributor, uniqueKey }: MockContributorAvatarProps) {
    return (
      <div data-testid="contributor-avatar" data-key={uniqueKey}>
        {contributor.login}
      </div>
    )
  }
})

jest.mock('components/DisplayIcon', () => {
  return function DisplayIcon({ item, icons }: MockDisplayIconProps) {
    const activeIconCount = icons ? Object.keys(icons).length : 0
    return (
      <span data-testid="display-icon" data-item={item} data-active-icons={activeIconCount}>
        {item} ({activeIconCount} active)
      </span>
    )
  }
})

jest.mock('components/MarkdownWrapper', () => {
  return function Markdown({ content, className }: MockMarkdownProps) {
    return (
      <div data-testid="markdown" className={className}>
        {content}
      </div>
    )
  }
})

jest.mock('utils/urlIconMappings', () => ({
  getSocialIcon: jest.fn().mockReturnValue('mocked-social-icon'),
}))

jest.mock('utils/data', () => ({
  ICONS: {
    react: true,
    typescript: true,
    javascript: true,
    node: true,
  },
}))

describe('Card', () => {
  const baseProps: CardProps = {
    title: 'Test Project',
    url: 'https://github.com/test/project',
    summary: 'This is a test project summary',
    button: {
      label: 'View Project',
      url: 'https://github.com/test',
      icon: <span data-testid="button-icon">github</span>,
      onclick: jest.fn(),
    },
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders successfully with minimal required props', () => {
    render(<Card {...baseProps} />)

    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('This is a test project summary')).toBeInTheDocument()
    expect(screen.getByTestId('action-button')).toBeInTheDocument()
  })

  it('renders all text content correctly', () => {
    render(<Card {...baseProps} />)

    const titleLink = screen.getByRole('link', { name: 'Test Project' })
    expect(titleLink).toHaveAttribute('href', 'https://github.com/test/project')
    expect(screen.getByTestId('markdown')).toHaveTextContent('This is a test project summary')
  })

  it('conditionally renders level badge when provided', () => {
    const propsWithLevel = {
      ...baseProps,
      level: { level: 'Beginner', color: '#4CAF50', icon: 'leaf-icon' },
    }

    render(<Card {...propsWithLevel} />)
    expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    expect(screen.getByTestId('font-awesome-wrapper')).toBeInTheDocument()
  })

  it('does not render level badge when not provided', () => {
    render(<Card {...baseProps} />)
    expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
  })

  it('conditionally renders icons when provided', () => {
    const propsWithIcons = {
      ...baseProps,
      icons: { react: 'active', typescript: 'active' },
    }
    render(<Card {...propsWithIcons} />)
    expect(screen.getAllByTestId('display-icon')).toHaveLength(2)
    expect(screen.getByText('react (2 active)')).toBeInTheDocument()
  })

  it('does not render icons section when no icon is provided', () => {
    render(<Card {...baseProps} />)
    expect(screen.queryByTestId('display-icon')).not.toBeInTheDocument()
  })

  it('conditionally renders project name link when provided', () => {
    const propsWithProject = {
      ...baseProps,
      projectName: 'Open Source Initiative',
      projectLink: 'https://opensource.org',
    }

    render(<Card {...propsWithProject} />)
    const projectLink = screen.getByRole('link', { name: 'Open Source Initiative' })
    expect(projectLink).toHaveAttribute('href', 'https://opensource.org')
  })

  it('does not render project name when not provided', () => {
    render(<Card {...baseProps} />)
    const allLinks = screen.getAllByRole('link')
    expect(allLinks).toHaveLength(1)
  })

  it('conditionally renders social icons when provided', () => {
    const propsWithSocial = {
      ...baseProps,
      social: [
        { title: 'GitHub', url: 'https://github.com/test', icon: 'github' },
        { title: 'Twitter', url: 'https://twitter.com/test', icon: 'twitter' },
      ],
    }
    render(<Card {...propsWithSocial} />)
    expect(screen.getAllByTestId('font-awesome-icon')).toHaveLength(2)

    const allLinks = screen.getAllByRole('link')
    expect(allLinks.length).toBeGreaterThan(1)
  })

  it('does not render social section when not provided', () => {
    render(<Card {...baseProps} />)
    expect(screen.queryByTestId('font-awesome-icon')).not.toBeInTheDocument()
  })

  it('conditionally renders project name when provided', () => {
    const propsWithProject = {
      ...baseProps,
      projectName: 'Test Organization',
      projectLink: 'https://test-org.com',
    }

    render(<Card {...propsWithProject} />)

    const projectLink = screen.getByRole('link', { name: 'Test Organization' })
    expect(projectLink).toHaveAttribute('href', 'https://test-org.com')
  })

  it('renders project name without link when projectLink is missing', () => {
    const propsWithProjectNameOnly = {
      ...baseProps,
      projectName: 'Test Organization',
    }

    render(<Card {...propsWithProjectNameOnly} />)

    expect(screen.getByText('Test Organization')).toBeInTheDocument()
    expect(screen.getAllByRole('link')).toHaveLength(1)
  })

  it('conditionally renders contributor avatars', () => {
    const propsWithContributors = {
      ...baseProps,
      topContributors: [
        {
          login: 'user1',
          name: 'User One',
          avatarUrl: 'https://github.com/user1.png',
          projectKey: 'project1',
        },
        {
          login: 'user2',
          name: 'User Two',
          avatarUrl: 'https://github.com/user2.png',
          projectKey: 'project2',
        },
      ],
    }
    render(<Card {...propsWithContributors} />)
    expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(2)
    expect(screen.getByText('user1')).toBeInTheDocument()
  })

  it('applies different level badge colors based on props', () => {
    const propsWithLevel = {
      ...baseProps,
      level: { level: 'Advanced', color: '#FF5722', icon: 'fire-icon' },
    }

    render(<Card {...propsWithLevel} />)
    const badge = screen.getByTestId('tooltip').firstChild as HTMLElement
    expect(badge).toHaveStyle({ backgroundColor: '#FF5722' })
  })

  it('handles action button click events', () => {
    const mockOnClick = jest.fn()
    const propsWithClickHandler = {
      ...baseProps,
      button: { ...baseProps.button, onclick: mockOnClick },
    }

    render(<Card {...propsWithClickHandler} />)
    fireEvent.click(screen.getByTestId('action-button'))
    expect(mockOnClick).toHaveBeenCalledTimes(1)
  })

  it('handles contributors with empty login', () => {
    const propsWithPartialContributors = {
      ...baseProps,
      topContributors: [
        {
          login: '',
          name: 'Anonymous',
          avatarUrl: 'https://github.com/user1.png',
          projectKey: 'project-key-1',
        },
        {
          login: 'user2',
          name: 'User Two',
          avatarUrl: 'https://github.com/user2.png',
          projectKey: 'project-key-2',
        },
      ],
    }

    render(<Card {...propsWithPartialContributors} />)
    expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(2)
  })

  it('handles empty contributors array', () => {
    const propsWithEmptyContributors = {
      ...baseProps,
      topContributors: [],
    }
    render(<Card {...propsWithEmptyContributors} />)
    expect(screen.queryByTestId('contributor-avatar')).not.toBeInTheDocument()
  })

  it('handles single contributor', () => {
    const propsWithOneContributor = {
      ...baseProps,
      topContributors: [
        {
          login: 'singleuser',
          name: 'Single User',
          avatarUrl: 'https://github.com/single.png',
          projectKey: 'single-key',
        },
      ],
    }
    render(<Card {...propsWithOneContributor} />)
    expect(screen.getAllByTestId('contributor-avatar')).toHaveLength(1)
    expect(screen.getByText('singleuser')).toBeInTheDocument()
  })

  it('handles empty string values gracefully', () => {
    const propsWithEmptyStrings = {
      ...baseProps,
      title: '',
      summary: '',
      projectName: '',
    }
    render(<Card {...propsWithEmptyStrings} />)
    expect(screen.getByTestId('action-button')).toBeInTheDocument()
  })

  it('handles extremely long title text', () => {
    const longTitle = 'A'.repeat(500)
    const propsWithLongTitle = { ...baseProps, title: longTitle }

    render(<Card {...propsWithLongTitle} />)
    expect(screen.getByText(longTitle)).toBeInTheDocument()
  })

  it('handles missing button onclick gracefully', () => {
    const propsWithoutOnClick = {
      ...baseProps,
      button: {
        label: 'View Project',
        url: 'https://github.com/test',
        icon: <span data-testid="button-icon">github</span>,
      },
    }

    expect(() => render(<Card {...propsWithoutOnClick} />)).not.toThrow()
  })

  it('has proper accessibility attributes', () => {
    const propsWithTooltip = {
      ...baseProps,
      level: { level: 'Intermediate', color: '#2196F3', icon: 'star-icon' },
      tooltipLabel: 'Click to contribute',
    }

    render(<Card {...propsWithTooltip} />)
    const titleLink = screen.getByRole('link', { name: 'Test Project' })
    expect(titleLink).toHaveAttribute('rel', 'noopener noreferrer')
    expect(titleLink).toHaveAttribute('target', '_blank')
    expect(screen.getByTestId('tooltip')).toHaveAttribute('title', 'Intermediate project')
    expect(screen.getByTestId('action-button')).toHaveAttribute('title', 'Click to contribute')
  })

  it('maintains proper heading hierarchy', () => {
    render(<Card {...baseProps} />)
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('Test Project')
  })

  it('applies correct css classes to main container', () => {
    render(<Card {...baseProps} />)
    const cardContainer = screen.getByText('Test Project').closest('div')
    expect(cardContainer).toHaveClass('flex', 'items-center', 'gap-3')
  })

  it('applies responsive title styling', () => {
    render(<Card {...baseProps} />)

    const titleElement = screen.getByText('Test Project')
    expect(titleElement).toHaveClass(
      'text-base',
      'font-semibold',
      'text-blue-400',
      'hover:text-blue-600',
      'sm:text-lg',
      'lg:text-2xl'
    )
  })

  it('applies correct markdown styling', () => {
    render(<Card {...baseProps} />)

    const markdown = screen.getByTestId('markdown')
    expect(markdown).toHaveClass('mt-2', 'w-full', 'text-gray-600', 'dark:text-gray-300')
  })

  it('filters and passes icons correctly to DisplayIcon components', () => {
    const propsWithMixedIcons = {
      ...baseProps,
      icons: {
        react: 'active',
        javascript: 'active',
      },
    }

    render(<Card {...propsWithMixedIcons} />)

    // Should only render the active icons
    expect(screen.getAllByTestId('display-icon')).toHaveLength(2)
    expect(screen.getByText('react (2 active)')).toBeInTheDocument()
    expect(screen.getByText('javascript (2 active)')).toBeInTheDocument()
    expect(screen.queryByText(/typescript/)).not.toBeInTheDocument()
  })

  it('renders complete card with all optional props', () => {
    const fullProps = {
      ...baseProps,
      level: { level: 'Expert', color: '#9C27B0', icon: 'crown-icon' },
      icons: { react: 'active', typescript: 'active' },
      projectName: 'Full Stack Project',
      projectLink: 'https://fullstack.com',
      social: [{ title: 'GitHub', url: 'https://github.com/full', icon: 'active' }],
      topContributors: [
        {
          login: 'expert',
          avatarUrl: 'https://github.com/expert.png',
          name: 'John Doe',
          projectKey: 'test-key',
        },
      ],
      tooltipLabel: 'Expert level project',
    }

    render(<Card {...fullProps} />)
    expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    expect(screen.getAllByTestId('display-icon')).toHaveLength(2)
    expect(screen.getByRole('link', { name: 'Full Stack Project' })).toBeInTheDocument()
    expect(screen.getByTestId('font-awesome-icon')).toBeInTheDocument()
    expect(screen.getByTestId('contributor-avatar')).toBeInTheDocument()
  })
})
