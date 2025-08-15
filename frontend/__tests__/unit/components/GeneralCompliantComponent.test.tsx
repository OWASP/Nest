import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { faCertificate } from '@fortawesome/free-solid-svg-icons'
import { render, screen } from '@testing-library/react'
import React from 'react'

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
  icon: IconProp
  title: string
}

describe('GeneralCompliantComponent', () => {
  const baseProps: GeneralCompliantComponentProps = {
    compliant: true,
    icon: faCertificate,
    title: 'Test Title',
  }

  it('renders successfully with minimal required props', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} />)
    expect(container).toBeInTheDocument()
  })

  it('applies correct color for compliant=true', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} compliant={true} />)
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg).toHaveClass('text-green-400/80')
  })

  it('applies correct color for compliant=false', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} compliant={false} />)
    const svg = container.querySelector('svg')
    expect(svg).toBeInTheDocument()
    expect(svg).toHaveClass('text-red-400/80')
  })

  it('renders the correct icon structure', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} />)
    const icons = container.querySelectorAll('svg')
    expect(icons).toHaveLength(2)
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

  it('has accessible SVG icons', () => {
    const { container } = render(<GeneralCompliantComponent {...baseProps} />)
    const icons = container.querySelectorAll('svg[role="img"]')
    expect(icons).toHaveLength(2)
    expect(icons[0]).toHaveAttribute('aria-hidden', 'true')
    expect(icons[1]).toHaveAttribute('aria-hidden', 'true')
  })

  it('renders with custom icon', () => {
    const customIcon = faCertificate
    const { container } = render(<GeneralCompliantComponent {...baseProps} icon={customIcon} />)
    expect(container.querySelector('svg')).toBeInTheDocument()
  })
})
