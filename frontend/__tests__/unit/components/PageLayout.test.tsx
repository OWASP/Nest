import { render, screen } from '@testing-library/react'
import { usePathname } from 'next/navigation'
import PageLayout from 'components/PageLayout'
import '@testing-library/jest-dom'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('PageLayout', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders children components', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

    render(
      <PageLayout breadcrumbData={{ projectName: 'OWASP ZAP' }}>
        <div>Child Content</div>
      </PageLayout>
    )

    expect(screen.getByText('Child Content')).toBeInTheDocument()
  })

  test('renders breadcrumbs above children', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

    const { container } = render(
      <PageLayout breadcrumbData={{ projectName: 'OWASP ZAP' }}>
        <div>Child Content</div>
      </PageLayout>
    )

    const breadcrumbNav = container.querySelector('nav')
    const childContent = screen.getByText('Child Content')

    expect(breadcrumbNav?.compareDocumentPosition(childContent)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING
    )
  })

  describe('BreadcrumbData Prop Handling', () => {
    test('passes projectName to breadcrumbs', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      render(
        <PageLayout breadcrumbData={{ projectName: 'OWASP ZAP' }}>
          <div>Content</div>
        </PageLayout>
      )

      expect(screen.getByText('OWASP ZAP')).toBeInTheDocument()
    })

    test('passes memberName to breadcrumbs', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/members/bjornkimminich')

      render(
        <PageLayout breadcrumbData={{ memberName: 'Björn Kimminich' }}>
          <div>Content</div>
        </PageLayout>
      )

      expect(screen.getByText('Björn Kimminich')).toBeInTheDocument()
    })

    test('passes chapterName to breadcrumbs', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/chapters/bangalore')

      render(
        <PageLayout breadcrumbData={{ chapterName: 'Bangalore Chapter' }}>
          <div>Content</div>
        </PageLayout>
      )

      expect(screen.getByText('Bangalore Chapter')).toBeInTheDocument()
    })

    test('passes committeeName to breadcrumbs', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/committees/outreach')

      render(
        <PageLayout breadcrumbData={{ committeeName: 'Outreach Committee' }}>
          <div>Content</div>
        </PageLayout>
      )

      expect(screen.getByText('Outreach Committee')).toBeInTheDocument()
    })

    test('passes orgName and repoName for repository pages', () => {
      ;(usePathname as jest.Mock).mockReturnValue(
        '/organizations/cyclonedx/repositories/cyclonedx-python'
      )

      render(
        <PageLayout
          breadcrumbData={{
            orgName: 'CycloneDX BOM Standard',
            repoName: 'Cyclonedx Python',
          }}
        >
          <div>Content</div>
        </PageLayout>
      )

      expect(screen.getByText('CycloneDX BOM Standard')).toBeInTheDocument()
      expect(screen.getByText('Cyclonedx Python')).toBeInTheDocument()
    })

    test('handles undefined breadcrumbData', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/juice-shop')

      render(
        <PageLayout>
          <div>Content</div>
        </PageLayout>
      )

      expect(screen.getByText('Juice shop')).toBeInTheDocument()
    })

    test('handles partial breadcrumbData (wrong field for route type)', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      render(
        <PageLayout breadcrumbData={{ memberName: 'John Doe' }}>
          <div>Content</div>
        </PageLayout>
      )

      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })
})
