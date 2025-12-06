import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { BreadcrumbRoot, registerBreadcrumb } from 'contexts/BreadcrumbContext'
import { usePathname } from 'next/navigation'
import React, { useEffect } from 'react'
import BreadCrumbsWrapper from 'components/BreadCrumbsWrapper'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

// Wrapper with BreadcrumbRoot for context tests
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BreadcrumbRoot>{children}</BreadcrumbRoot>
)

// Helper component to register a breadcrumb before rendering BreadCrumbsWrapper
function BreadCrumbsWrapperWithTitle({ path, title }: Readonly<{ path: string; title: string }>) {
  useEffect(() => {
    const unregister = registerBreadcrumb({ path, title })
    return unregister
  }, [path, title])
  return <BreadCrumbsWrapper />
}

describe('BreadCrumbsWrapper', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Route Detection - Should Hide', () => {
    test('returns null on home page', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/')

      const { container } = render(<BreadCrumbsWrapper />)
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Route Detection - Should Render', () => {
    test('renders for routes with registered breadcrumbs', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects')

      render(<BreadCrumbsWrapperWithTitle path="/projects" title="Projects" />, { wrapper })
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('Projects')).toBeInTheDocument()
    })

    test('uses registered title', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/test-project-1')

      render(
        <BreadCrumbsWrapperWithTitle
          path="/projects/test-project-1"
          title="Security Scanner Tool"
        />,
        { wrapper }
      )
      // Should show registered title instead of URL slug
      expect(screen.getByText('Security Scanner Tool')).toBeInTheDocument()
    })
  })
})
