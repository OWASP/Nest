import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import React from 'react'
import { FaCode, FaTags } from 'react-icons/fa6'
import CardDetailsHeader from 'components/CardDetailsPage/CardDetailsHeader'
import CardDetailsMetadata from 'components/CardDetailsPage/CardDetailsMetadata'
import CardDetailsPageWrapper from 'components/CardDetailsPage/CardDetailsPageWrapper'
import CardDetailsSummary from 'components/CardDetailsPage/CardDetailsSummary'
import CardDetailsTags from 'components/CardDetailsPage/CardDetailsTags'

jest.mock('next/link', () => {
  return function MockLink({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode
    href: string
    [key: string]: unknown
  }) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

jest.mock('components/ChapterMapWrapper', () => ({
  __esModule: true,
  default: ({
    geoLocData: _geoLocData,
    showLocal,
    style,
    showLocationSharing: _showLocationSharing,
    ...otherProps
  }: {
    geoLocData?: unknown
    showLocal: boolean
    style: React.CSSProperties
    showLocationSharing?: boolean
    [key: string]: unknown
  }) => {
    return (
      <div data-testid="chapter-map-wrapper" style={style} {...otherProps}>
        Chapter Map {showLocal ? '(Local)' : ''}
      </div>
    )
  },
}))

jest.mock('react-apexcharts', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-chart" />,
}))

jest.mock('next/dynamic', () => ({
  __esModule: true,
  default: () => {
    return function MockDynamicComponent({
      children,
      ...props
    }: React.ComponentPropsWithoutRef<'div'>) {
      return <div {...props}>{children}</div>
    }
  },
}))

jest.mock('next-auth/react', () => ({
  useSession: jest.fn(() => ({ data: null, status: 'unauthenticated' })),
}))

jest.mock('@apollo/client/react', () => ({
  useMutation: jest.fn(() => [jest.fn()]),
}))

const mockStats = [
  {
    icon: FaCode,
    pluralizedName: 'repositories',
    unit: 'Repository',
    value: 10,
  },
  {
    icon: FaTags,
    pluralizedName: 'Stars',
    unit: 'Star',
    value: 100,
  },
]

const mockDetails = [
  { label: 'Created', value: '2023-01-01' },
  { label: 'Leaders', value: 'John Doe, Jane Smith' },
  { label: 'Status', value: 'Active' },
]

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('CardDetailsPage a11y ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })

  it('should have no accessibility violations in header', async () => {
    const { container } = render(
      <CardDetailsPageWrapper>
        <CardDetailsHeader title="Test Project" isActive={true} isArchived={false} />
      </CardDetailsPageWrapper>
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations in summary', async () => {
    const { container } = render(
      <CardDetailsPageWrapper>
        <CardDetailsSummary summary="A test project for demonstration" />
      </CardDetailsPageWrapper>
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations in metadata', async () => {
    const { container } = render(
      <CardDetailsPageWrapper>
        <CardDetailsMetadata details={mockDetails} stats={mockStats} detailsTitle="Details" />
      </CardDetailsPageWrapper>
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations in tags', async () => {
    const { container } = render(
      <CardDetailsPageWrapper>
        <CardDetailsTags languages={['JavaScript', 'TypeScript']} topics={['web', 'frontend']} />
      </CardDetailsPageWrapper>
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have no violations for complete page layout', async () => {
    const { container } = render(
      <CardDetailsPageWrapper>
        <CardDetailsHeader title="Test Project" isActive={true} isArchived={false} />
        <CardDetailsSummary summary="A test project for demonstration" />
        <CardDetailsMetadata details={mockDetails} stats={mockStats} detailsTitle="Details" />
        <CardDetailsTags languages={['JavaScript']} topics={['web']} />
      </CardDetailsPageWrapper>
    )
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
