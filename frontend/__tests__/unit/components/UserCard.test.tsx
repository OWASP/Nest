import { render, screen, fireEvent, cleanup } from '@testing-library/react'
import React from 'react'
import type { UserCardProps } from 'types/card'
import UserCard from 'components/UserCard'

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    fill,
    objectFit,
    ...props
  }: {
    src: string
    alt: string
    fill?: boolean
    objectFit?: 'fill' | 'contain' | 'cover' | 'none' | 'scale-down'
    [key: string]: unknown
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      style={fill ? { objectFit: objectFit as React.CSSProperties['objectFit'] } : undefined}
      data-testid="user-avatar"
      {...props}
    />
  ),
}))

jest.mock('@heroui/button', () => {
  const MockButton = ({
    children,
    onPress,
    className,
    ...props
  }: {
    children: React.ReactNode
    onPress?: () => void
    className?: string
    [key: string]: unknown
  }) => (
    <button onClick={onPress} className={className} {...props}>
      {children}
    </button>
  )
  MockButton.displayName = 'MockButton'
  return {
    __esModule: true,
    // eslint-disable-next-line @typescript-eslint/naming-convention
    Button: MockButton,
  }
})

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({
    icon,
    className,
    ...props
  }: {
    icon: { iconName: string }
    className?: string
    [key: string]: unknown
  }) => <span data-testid={`icon-${icon.iconName}`} className={className} {...props} />,
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div data-testid="tooltip" data-tooltip-content={content}>
      {children}
    </div>
  ),
}))

jest.mock('millify', () => ({
  __esModule: true,
  default: (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `${(value / 1000).toFixed(1)}k`
    return value.toString()
  },
}))

describe('UserCard', () => {
  const mockButtonClick = jest.fn()
  const defaultProps: UserCardProps = {
    name: 'John Doe',
    avatar: '',
    button: {
      label: 'View Profile',
      onclick: mockButtonClick,
    },
    className: '',
    company: '',
    description: '',
    email: '',
    followersCount: 0,
    location: '',
    repositoriesCount: 0,
    badgeCount: 0,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  afterEach(() => {
    cleanup()
  })

  describe('Essential Rendering Tests', () => {
    it('renders successfully with minimal required props', () => {
      render(<UserCard {...defaultProps} />)

      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('View Profile')).toBeInTheDocument()
      expect(screen.getByTestId('icon-chevron-right')).toBeInTheDocument()
    })

    it('renders with all props provided', () => {
      const fullProps: UserCardProps = {
        ...defaultProps,
        avatar: 'https://example.com/avatar.jpg',
        className: 'custom-class',
        company: 'Tech Corp',
        description: 'Software Developer',
        email: 'john@example.com',
        followersCount: 1500,
        location: 'San Francisco, CA',
        repositoriesCount: 25,
        badgeCount: 5,
        button: {
          label: 'View Profile',
          onclick: mockButtonClick,
        },
      }

      render(<UserCard {...fullProps} />)

      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText(/Tech Corp/)).toBeInTheDocument()
      expect(screen.getByText('Software Developer')).toBeInTheDocument()
      expect(screen.getByTestId('user-avatar')).toHaveAttribute(
        'src',
        'https://example.com/avatar.jpg&s=160'
      )
      expect(screen.getByText('1.5k')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
    })
  })

  describe('Conditional Rendering Logic', () => {
    it('renders avatar image when avatar prop is provided', () => {
      render(<UserCard {...defaultProps} avatar="https://example.com/avatar.jpg" />)

      const avatarImage = screen.getByTestId('user-avatar')
      expect(avatarImage).toBeInTheDocument()
      expect(avatarImage).toHaveAttribute('src', 'https://example.com/avatar.jpg&s=160')
      expect(avatarImage).toHaveAttribute('alt', "John Doe's profile picture")
    })

    it('renders default user icon when avatar is empty string', () => {
      render(<UserCard {...defaultProps} avatar="" />)

      expect(screen.queryByTestId('user-avatar')).not.toBeInTheDocument()
      expect(screen.getByTestId('icon-user')).toBeInTheDocument()
    })

    it('renders company information when provided', () => {
      render(<UserCard {...defaultProps} company="Tech Corp" />)

      expect(screen.getByText(/Tech Corp/)).toBeInTheDocument()
    })

    it('renders location when company is not provided', () => {
      render(<UserCard {...defaultProps} location="New York, NY" />)

      expect(screen.getByText('New York, NY')).toBeInTheDocument()
    })

    it('renders email when company and location are not provided', () => {
      render(<UserCard {...defaultProps} email="john@example.com" />)

      expect(screen.getByText('john@example.com')).toBeInTheDocument()
    })

    it('renders login  when company and location and email are not provided', () => {
      render(<UserCard {...defaultProps} login="login" />)

      expect(screen.getByText('login')).toBeInTheDocument()
    })

    it('prioritizes company over location and email', () => {
      render(
        <UserCard
          {...defaultProps}
          company="Tech Corp"
          location="New York, NY"
          email="john@example.com"
        />
      )

      expect(screen.getByText('Tech Corp')).toBeInTheDocument()
      expect(screen.queryByText('New York, NY')).not.toBeInTheDocument()
      expect(screen.queryByText('john@example.com')).not.toBeInTheDocument()
    })

    it('renders description when provided', () => {
      render(<UserCard {...defaultProps} description="Full Stack Developer" />)

      expect(screen.getByText('Full Stack Developer')).toBeInTheDocument()
    })

    it('does not render description when not provided', () => {
      render(<UserCard {...defaultProps} />)

      expect(screen.queryByText('Full Stack Developer')).not.toBeInTheDocument()
    })

    it('renders followers count when greater than 0', () => {
      render(<UserCard {...defaultProps} followersCount={1200} />)

      expect(screen.getByText('1.2k')).toBeInTheDocument()
      expect(screen.getByTestId('icon-users')).toBeInTheDocument()
    })

    it('does not render followers count when 0', () => {
      render(<UserCard {...defaultProps} followersCount={0} />)

      expect(screen.queryByTestId('icon-users')).not.toBeInTheDocument()
    })

    it('renders repositories count when greater than 0', () => {
      render(<UserCard {...defaultProps} repositoriesCount={42} />)

      expect(screen.getByText('42')).toBeInTheDocument()
      expect(screen.getByTestId('icon-folder-open')).toBeInTheDocument()
    })

    it('does not render repositories count when 0', () => {
      render(<UserCard {...defaultProps} repositoriesCount={0} />)

      expect(screen.queryByTestId('icon-folder-open')).not.toBeInTheDocument()
    })

    it('renders both followers and repositories when both are greater than 0', () => {
      render(<UserCard {...defaultProps} followersCount={500} repositoriesCount={25} />)

      expect(screen.getByText('500')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
      expect(screen.getByTestId('icon-users')).toBeInTheDocument()
      expect(screen.getByTestId('icon-folder-open')).toBeInTheDocument()
    })
  })

  describe('Event Handling', () => {
    it('calls button onclick handler when card is clicked', () => {
      render(<UserCard {...defaultProps} />)

      const button = screen.getByRole('button')
      fireEvent.click(button)

      expect(mockButtonClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('Text and Content Rendering', () => {
    it('renders username correctly', () => {
      render(<UserCard {...defaultProps} name="Jane Smith" />)

      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
    })

    it('uses name as avatar alt text', () => {
      render(
        <UserCard {...defaultProps} name="Jane Smith" avatar="https://example.com/avatar.jpg" />
      )

      expect(screen.getByTestId('user-avatar')).toHaveAttribute(
        'alt',
        "Jane Smith's profile picture"
      )
    })

    it('uses fallback alt text when name is not provided', () => {
      render(<UserCard {...defaultProps} name="" avatar="https://example.com/avatar.jpg" />)

      expect(screen.getByTestId('user-avatar')).toHaveAttribute('alt', 'User profile picture')
    })

    it('displays View Profile text', () => {
      render(<UserCard {...defaultProps} />)

      expect(screen.getByText('View Profile')).toBeInTheDocument()
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('handles undefined name gracefully', () => {
      render(<UserCard {...defaultProps} name={undefined as unknown as string} />)

      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('handles negative followers count', () => {
      render(<UserCard {...defaultProps} followersCount={-5} />)

      expect(screen.queryByTestId('icon-users')).not.toBeInTheDocument()
    })

    it('handles negative repositories count', () => {
      render(<UserCard {...defaultProps} repositoriesCount={-10} />)

      expect(screen.queryByTestId('icon-folder-open')).not.toBeInTheDocument()
    })

    it('handles very large numbers with millify', () => {
      render(<UserCard {...defaultProps} followersCount={1500000} repositoriesCount={2500} />)

      expect(screen.getByText('1.5M')).toBeInTheDocument()
      expect(screen.getByText('2.5k')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('renders as a button with proper role', () => {
      render(<UserCard {...defaultProps} />)

      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    it('has accessible avatar image', () => {
      render(<UserCard {...defaultProps} name="John Doe" avatar="https://example.com/avatar.jpg" />)

      const avatar = screen.getByTestId('user-avatar')
      expect(avatar).toHaveAttribute('alt', "John Doe's profile picture")
    })

    it('maintains semantic heading structure', () => {
      render(<UserCard {...defaultProps} name="John Doe" />)

      const heading = screen.getByRole('heading', { level: 3 })
      expect(heading).toHaveTextContent('John Doe')
    })
  })

  describe('DOM Structure and Styling', () => {
    it('applies custom className when provided', () => {
      render(<UserCard {...defaultProps} className="custom-test-class" />)

      const button = screen.getByRole('button')
      expect(button).toHaveClass('custom-test-class')
    })

    it('applies default classes', () => {
      render(<UserCard {...defaultProps} />)

      const button = screen.getByRole('button')
      expect(button).toHaveClass(
        'group',
        'flex',
        'flex-col',
        'items-center',
        'rounded-lg',
        'px-6',
        'py-6'
      )
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('shows default user icon when no avatar is provided', () => {
      render(<UserCard {...defaultProps} avatar="" />)

      expect(screen.getByTestId('icon-user')).toBeInTheDocument()
    })

    it('shows no secondary info when company, location, and email are empty', () => {
      render(<UserCard {...defaultProps} company="" location="" email="" />)

      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('View Profile')).toBeInTheDocument()
    })

    it('defaults followers and repositories to not showing when 0', () => {
      render(<UserCard {...defaultProps} followersCount={0} repositoriesCount={0} />)

      expect(screen.queryByTestId('icon-users')).not.toBeInTheDocument()
      expect(screen.queryByTestId('icon-folder-open')).not.toBeInTheDocument()
    })
  })

  describe('Data Processing', () => {
    it('appends size parameter to avatar URL', () => {
      render(<UserCard {...defaultProps} avatar="https://example.com/avatar.jpg" />)

      const avatar = screen.getByTestId('user-avatar')
      expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.jpg&s=160')
    })

    it('formats large numbers with millify precision', () => {
      render(<UserCard {...defaultProps} followersCount={1234} repositoriesCount={5678} />)

      expect(screen.getByText('1.2k')).toBeInTheDocument()
      expect(screen.getByText('5.7k')).toBeInTheDocument()
    })
  })

  describe('Badge Count Display', () => {
    it('renders badge count when greater than 0', () => {
      render(<UserCard {...defaultProps} badgeCount={5} />)

      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
    })

    it('does not render badge count when 0', () => {
      render(<UserCard {...defaultProps} badgeCount={0} />)

      expect(screen.queryByTestId('icon-medal')).not.toBeInTheDocument()
    })

    it('renders all three metrics when all are greater than 0', () => {
      render(
        <UserCard {...defaultProps} followersCount={100} repositoriesCount={50} badgeCount={3} />
      )

      expect(screen.getByTestId('icon-users')).toBeInTheDocument()
      expect(screen.getByTestId('icon-folder-open')).toBeInTheDocument()
      expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
    })

    it('formats badge count with millify for large numbers', () => {
      render(<UserCard {...defaultProps} badgeCount={1500} />)

      expect(screen.getByText('1.5k')).toBeInTheDocument()
    })

    it('handles negative badge count', () => {
      render(<UserCard {...defaultProps} badgeCount={-1} />)

      expect(screen.queryByTestId('icon-medal')).not.toBeInTheDocument()
    })
  })
})
