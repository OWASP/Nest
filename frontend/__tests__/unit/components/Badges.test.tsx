import { render, screen } from '@testing-library/react'
import React from 'react'
import Badges from 'components/Badges'

// Mock FontAwesome
jest.mock('@fortawesome/fontawesome-svg-core', () => ({
  findIconDefinition: jest.fn(({ iconName }: { iconName: string }) => {
    // Return truthy value for valid icons, null for invalid
    return iconName === 'medal' ? { iconName } : null
  }),
}))

jest.mock('wrappers/FontAwesomeIconWrapper', () => {
  return function MockFontAwesomeIconWrapper({ icon }: { icon: string }) {
    const iconName = icon.split(' ').pop()?.replace('fa-', '') || icon.replace('fa-', '')
    return <span data-testid={`icon-${iconName}`} />
  }
})

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({
    children,
    content,
    isDisabled,
  }: {
    children: React.ReactNode
    content: string
    isDisabled?: boolean
  }) => {
    if (isDisabled) {
      return <>{children}</>
    }
    return (
      <div data-testid="tooltip" data-content={content}>
        {children}
      </div>
    )
  },
}))

describe('Badges Component', () => {
  const defaultProps = {
    name: 'Test Badge',
    cssClass: 'fa-solid fa-medal',
  }

  it('renders valid icon with tooltip', () => {
    render(<Badges {...defaultProps} />)

    expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
    expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Test Badge')
  })

  it('renders fallback fa-medal for invalid cssClass', () => {
    render(<Badges {...defaultProps} cssClass="" />)

    expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
  })

  it('renders fa-question fallback for unrecognized icon', () => {
    render(<Badges {...defaultProps} cssClass="fa-solid fa-unknown" />)

    expect(screen.getByTestId('icon-question')).toBeInTheDocument()
  })

  it('hides tooltip when showTooltip is false', () => {
    render(<Badges {...defaultProps} showTooltip={false} />)

    expect(screen.getByTestId('icon-medal')).toBeInTheDocument()
    expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
  })
})
