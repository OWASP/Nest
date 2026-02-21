import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { BreadcrumbRoot } from 'contexts/BreadcrumbContext'
import { usePathname } from 'next/navigation'
import React from 'react'
import BreadCrumbsWrapper from 'components/BreadCrumbsWrapper'
import PageLayout from 'components/PageLayout'

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

// Helper to wrap components with BreadcrumbRoot and render with BreadCrumbsWrapper
const renderWithProvider = (ui: React.ReactElement) => {
  return render(
    <BreadcrumbRoot>
      <BreadCrumbsWrapper />
      {ui}
    </BreadcrumbRoot>
  )
}

describe('PageLayout', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders children components', () => {
    ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

    renderWithProvider(
      <PageLayout title="OWASP ZAP">
        <div>Child Content</div>
      </PageLayout>
    )

    expect(screen.getByText('Child Content')).toBeInTheDocument()
  })

  describe('Title Prop Handling', () => {
    test('displays title in breadcrumbs', async () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      renderWithProvider(
        <PageLayout title="OWASP ZAP">
          <div>Content</div>
        </PageLayout>
      )

      // Wait for effect to run
      await screen.findByText('OWASP ZAP')
      expect(screen.getByText('OWASP ZAP')).toBeInTheDocument()
    })

    test('handles explicit path prop', async () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap/details')

      renderWithProvider(
        <PageLayout title="OWASP ZAP" path="/projects/zap">
          <div>Content</div>
        </PageLayout>
      )

      await screen.findByText('OWASP ZAP')
      expect(screen.getByText('OWASP ZAP')).toBeInTheDocument()
    })
  })

  describe('breadcrumbClassName', () => {
    test('applies default breadcrumb class when breadcrumbClassName is not passed', async () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      renderWithProvider(
        <PageLayout title="OWASP ZAP">
          <div>Content</div>
        </PageLayout>
      )

      await screen.findByRole('navigation', { name: 'breadcrumb' })
      const breadcrumbNav = screen.getByRole('navigation', { name: 'breadcrumb' })
      const wrapper = breadcrumbNav.parentElement?.parentElement
      expect(wrapper).toHaveClass('bg-white')
      expect(wrapper).toHaveClass('dark:bg-[#212529]')
    })

    test('applies custom breadcrumb class when breadcrumbClassName is passed', async () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/zap')

      renderWithProvider(
        <PageLayout title="OWASP ZAP" breadcrumbClassName="custom-bg">
          <div>Content</div>
        </PageLayout>
      )

      await screen.findByRole('navigation', { name: 'breadcrumb' })
      const breadcrumbNav = screen.getByRole('navigation', { name: 'breadcrumb' })
      const wrapper = breadcrumbNav.parentElement?.parentElement
      expect(wrapper).toHaveClass('custom-bg')
    })
  })
})
