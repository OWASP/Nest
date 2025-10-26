import { render, screen } from '@testing-library/react'
import React from 'react'
import Badges from 'components/Badges'

jest.mock('wrappers/FontAwesomeIconWrapper', () => {
  const RealWrapper = jest.requireActual('wrappers/FontAwesomeIconWrapper').default

  const getName = (icon) => {
    if (!icon) return 'medal'
    if (typeof icon === 'string') {
      const m = icon.match(/fa-([a-z0-9-]+)$/i)
      if (m) return m[1]
      const last = icon.trim().split(/\s+/).pop() || ''
      return last.replace(/^fa-/, '') || 'medal'
    }
    if (Array.isArray(icon) && icon.length >= 2) return String(icon[1])
    if (icon && typeof icon === 'object') return icon.iconName || String(icon[1] ?? 'medal')
    return 'medal'
  }

  return function MockFontAwesomeIconWrapper(props) {
    const name = getName(props.icon)
    return (
      <div data-testid={`icon-${name}`}>
        <RealWrapper {...props} />
      </div>
    )
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

//only for confirming the badges are working properly
describe('Badges Component', () => {
  const defaultProps = {
    name: 'Test Badge',
    cssClass: 'medal',
  }

  it('renders valid icon with tooltip', () => {
    render(<Badges {...defaultProps} />)

    const icon = screen.getByTestId('badge-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('data-icon', 'medal')
    expect(screen.getByTestId('tooltip')).toHaveAttribute('data-content', 'Test Badge')
  })

  it('renders fallback fa-medal for invalid cssClass', () => {
    render(<Badges {...defaultProps} cssClass="" />)

    const icon = screen.getByTestId('badge-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('data-icon', 'medal')
  })

  it('renders fallback medal for unrecognized icon', () => {
    render(<Badges {...defaultProps} cssClass="unknown-icon" />)

    const icon = screen.getByTestId('badge-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('data-icon', 'medal')
  })

  it('hides tooltip when showTooltip is false', () => {
    render(<Badges {...defaultProps} showTooltip={false} />)

    const icon = screen.getByTestId('badge-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('data-icon', 'medal')
    expect(screen.queryByTestId('tooltip')).not.toBeInTheDocument()
  })

  describe('Backend enum icons', () => {
    const backendIcons = [
      { cssClass: 'award', expectedIcon: 'award' },
      { cssClass: 'medal', expectedIcon: 'medal' },
      { cssClass: 'ribbon', expectedIcon: 'ribbon' },
      { cssClass: 'star', expectedIcon: 'star' },
      { cssClass: 'certificate', expectedIcon: 'certificate' },
      { cssClass: 'bug_slash', expectedIcon: 'bug' }, // Backend snake_case input
    ]

    for (const backendIcon of backendIcons) {
       it(`renders ${backendIcon.cssClass} icon correctly (transforms snake_case to camelCase)`, () => {
        render(<Badges name={`${backendIcon.cssClass} Badge`} cssClass={backendIcon.cssClass} />)

        const icon = screen.getByTestId('badge-icon')
        expect(icon).toBeInTheDocument()
        expect(icon).toHaveAttribute('data-icon', backendIcon.expectedIcon)
      })
    }
 
    it('handles camelCase input directly', () => {
      render(<Badges name="Bug Slash Badge" cssClass="bugSlash" />)

      const icon = screen.getByTestId('badge-icon')
      expect(icon).toBeInTheDocument()
      expect(icon).toHaveAttribute('data-icon', 'bug')
    })
  })
})
