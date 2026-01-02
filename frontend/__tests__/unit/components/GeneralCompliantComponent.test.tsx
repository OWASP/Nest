import { render, screen } from '@testing-library/react'
import React from 'react'
import type { IconType } from 'react-icons'
import { FaCertificate } from 'react-icons/fa6'

import '@testing-library/jest-dom'

// Mock the Tooltip component to prevent async state update warnings
jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <div data-testid="tooltip" title={content}>
      {children}
    </div>
  ),
}))

import GeneralCompliantComponent from 'components/GeneralCompliantComponent'

type GeneralCompliantComponentProps = {
  compliant: boolean
  icon: IconType
  title: string
}

describe('GeneralCompliantComponent', () => {
  const baseProps: GeneralCompliantComponentProps = {
    compliant: true,
    icon: FaCertificate,
    title: 'Test Title',
  }

  it('renders successfully with minimal required props', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} />)
    expect(container).toBeInTheDocument()
  })

  it('applies correct background color for compliant=true', () => {
    render(<GeneralCompliantComponent {...baseProps} compliant={true} />)

    const badgeContainer = screen.getByTestId('tooltip').firstElementChild

    expect(badgeContainer).toBeInTheDocument()
    expect(badgeContainer).toHaveClass('bg-green-400/80')
    expect(badgeContainer).toHaveClass('text-green-900/90')
  })

  it('applies correct background color for compliant=false', () => {
    render(<GeneralCompliantComponent {...baseProps} compliant={false} />)

    const badgeContainer = screen.getByTestId('tooltip').firstElementChild

    expect(badgeContainer).toBeInTheDocument()
    expect(badgeContainer).toHaveClass('bg-red-400/80')
    expect(badgeContainer).toHaveClass('text-red-900/90')
  })

  it('renders exactly one icon (the inner symbol)', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} />)
    const icons = container.querySelectorAll('svg')
    expect(icons).toHaveLength(1)
  })

  it('renders tooltip wrapper with title attribute', () => {
    render(<GeneralCompliantComponent {...baseProps} title="Tooltip Title" />)
    const tooltip = screen.getByTestId('tooltip')
    expect(tooltip).toBeInTheDocument()
    expect(tooltip).toHaveAttribute('title', 'Tooltip Title')
  })

  it('handles edge case: empty title', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} title="" />)
    expect(container).toBeInTheDocument()
  })
})
