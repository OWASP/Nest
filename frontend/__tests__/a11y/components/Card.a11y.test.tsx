import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { ReactNode } from 'react'
import { FaCrown } from 'react-icons/fa6'
import Card from 'components/Card'

interface MockLinkProps {
  children: ReactNode
  href: string
  target?: string
  rel?: string
  className?: string
}

jest.mock('components/MarkdownWrapper', () => ({
  __esModule: true,
  default: ({ children }) => <div>{children}</div>,
}))

jest.mock('next/link', () => {
  return function MockedLink({ children, href, ...props }: MockLinkProps) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

const baseProps = {
  cardKey: 'test-card-1',
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

describe('Card Accessibility', () => {
  it('should not have any accessibility violations with minimal props', async () => {
    const { container } = render(<Card {...baseProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when level is provided', async () => {
    const { container } = render(
      <Card
        {...baseProps}
        cardKey="test-card-2"
        level={{ level: 'Expert', color: '#9C27B0', icon: FaCrown }}
      />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when project name is provided', async () => {
    const { container } = render(
      <Card {...baseProps} cardKey="test-card-3" projectName="Test Organization" />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when socials is provided', async () => {
    const { container } = render(
      <Card
        {...baseProps}
        cardKey="test-card-4"
        social={[{ title: 'GitHub', url: 'https://github.com/test', icon: FaCrown }]}
      />
    )

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
