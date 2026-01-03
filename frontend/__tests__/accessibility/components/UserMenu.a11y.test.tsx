import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { ReactNode } from 'react'
import UserMenu from 'components/UserMenu'

expect.extend(toHaveNoViolations)

jest.mock('hooks/useDjangoSession', () => ({
  useDjangoSession: () => ({
    session: {
      user: {
        name: 'John Doe',
        email: 'john@example.com',
        image: 'https://example.com/avatar.jpg',
        isOwaspStaff: true,
      },
      expires: '2024-12-31',
    },
    isSyncing: false,
    status: 'authenticated',
  }),
}))

jest.mock('hooks/useLogout', () => ({
  useLogout: () => ({
    logout: jest.fn(),
    isLoggingOut: false,
  }),
}))

jest.mock(
  'next/link',
  () =>
    ({
      children,
      href,
      ...props
    }: {
      children: ReactNode
      href: string
      [key: string]: unknown
    }) => (
      <a href={href} {...props}>
        {children}
      </a>
    )
)

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    className,
    height,
    width,
    ...props
  }: {
    src: string
    alt: string
    className?: string
    height?: number
    width?: number
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} className={className} height={height} width={width} {...props} />
  ),
}))

describe('UserMenu Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<UserMenu isGitHubAuthEnabled={true} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
