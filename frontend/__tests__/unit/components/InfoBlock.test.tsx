import { faUser, faStar, faCode } from '@fortawesome/free-solid-svg-icons'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import millify from 'millify'
import React from 'react'
import { pluralize } from 'utils/pluralize'
import InfoBlock from 'components/InfoBlock'

jest.mock('millify', () => jest.fn())
jest.mock('utils/pluralize', () => ({
  pluralize: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({
    icon,
    className,
    ...props
  }: {
    icon: { iconName: string }
    className?: string
    [key: string]: unknown
  }) => <span data-testid={`icon-${icon.iconName}`} className={className} {...props} />,
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) => (
    <span data-testid="tooltip" title={content}>
      {children}
    </span>
  ),
}))

const mockMillify = millify as jest.Mock
const mockPluralize = pluralize as jest.Mock

describe('InfoBlock Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockMillify.mockReturnValue('1k')
    mockPluralize.mockReturnValue('users')
  })

  describe('Essential Test Coverage', () => {
    describe('Renders successfully with minimal required props', () => {
      it('should render with only required props (icon and value)', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={100} />)

        expect(screen.getByTestId('icon-user')).toBeInTheDocument()
        expect(screen.getByText('100 items')).toBeInTheDocument()
        expect(screen.getByTestId('tooltip')).toBeInTheDocument()
      })

      it('should render with all props provided', () => {
        mockMillify.mockReturnValue('1.5k')
        mockPluralize.mockReturnValue('contributors')

        render(
          <InfoBlock
            icon={faStar}
            value={1500}
            unit="contributor"
            pluralizedName="contributors"
            precision={2}
            label="Team Members"
            className="custom-class"
          />
        )

        expect(screen.getByTestId('icon-star')).toBeInTheDocument()
        expect(screen.getByText('Team Members')).toBeInTheDocument()
        expect(screen.getByText('1.5k contributors')).toBeInTheDocument()
      })
    })

    describe('Conditional rendering logic', () => {
      it('should show label when provided', () => {
        mockMillify.mockReturnValue('50')
        mockPluralize.mockReturnValue('projects')

        render(<InfoBlock icon={faCode} value={50} label="Active Projects" />)

        expect(screen.getByText('Active Projects')).toBeInTheDocument()
        expect(screen.getByText('Active Projects')).toHaveClass('text-sm', 'font-medium')
      })

      it('should not show label when not provided', () => {
        mockMillify.mockReturnValue('50')
        mockPluralize.mockReturnValue('projects')

        render(<InfoBlock icon={faCode} value={50} />)

        expect(screen.queryByText('Active Projects')).not.toBeInTheDocument()
      })

      it('should show "No" prefix when value is 0', () => {
        mockMillify.mockReturnValue('0')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={0} />)

        expect(screen.getByText('No items')).toBeInTheDocument()
      })

      it('should show normal format when value is greater than 0', () => {
        mockMillify.mockReturnValue('5')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={5} />)

        expect(screen.getByText('5 items')).toBeInTheDocument()
        expect(screen.queryByText('No items')).not.toBeInTheDocument()
      })
    })

    describe('Prop-based behavior', () => {
      it('should use custom className when provided', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('users')

        const { container } = render(
          <InfoBlock icon={faUser} value={100} className="custom-spacing pb-4" />
        )

        const wrapper = container.firstChild as HTMLElement
        expect(wrapper).toHaveClass('flex', 'custom-spacing', 'pb-4')
      })

      it('should use default className when not provided', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('users')

        const { container } = render(<InfoBlock icon={faUser} value={100} />)

        const wrapper = container.firstChild as HTMLElement
        expect(wrapper).toHaveClass('flex')
        expect(wrapper).not.toHaveClass('custom-spacing')
      })

      it('should pass precision to millify function', () => {
        mockMillify.mockReturnValue('1.234k')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={1234} precision={3} />)

        expect(mockMillify).toHaveBeenCalledWith(1234, { precision: 3 })
      })

      it('should use default precision of 1 when not provided', () => {
        mockMillify.mockReturnValue('1.2k')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={1234} />)

        expect(mockMillify).toHaveBeenCalledWith(1234, { precision: 1 })
      })

      it('should use pluralizedName when provided', () => {
        mockMillify.mockReturnValue('5')
        mockPluralize.mockReturnValue('people')

        render(<InfoBlock icon={faUser} value={5} unit="person" pluralizedName="people" />)

        expect(mockPluralize).toHaveBeenCalledWith(5, 'person', 'people')
      })

      it('should use default pluralization when pluralizedName not provided', () => {
        mockMillify.mockReturnValue('5')
        mockPluralize.mockReturnValue('users')

        render(<InfoBlock icon={faUser} value={5} unit="user" />)

        expect(mockPluralize).toHaveBeenCalledWith(5, 'user')
      })
    })

    describe('Event handling', () => {
      it('should handle tooltip hover interactions', async () => {
        const user = userEvent.setup()
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={100} />)

        const tooltip = screen.getByTestId('tooltip')

        // Verify tooltip is initially present
        expect(tooltip).toBeInTheDocument()
        expect(tooltip).toHaveAttribute('title', '100 items')

        await user.hover(tooltip)
        // Tooltip should remain accessible and maintain its content
        expect(tooltip).toBeInTheDocument()
        expect(tooltip).toHaveAttribute('title', '100 items')

        fireEvent.mouseLeave(tooltip)
        // Tooltip should still be present with correct content after mouse leave
        expect(tooltip).toBeInTheDocument()
        expect(tooltip).toHaveAttribute('title', '100 items')
      })

      it('should handle tooltip click interactions', async () => {
        const user = userEvent.setup()
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={100} />)

        const tooltip = screen.getByTestId('tooltip')

        // Verify tooltip is accessible for interaction
        expect(tooltip).toBeInTheDocument()
        expect(tooltip).toHaveAttribute('title', '100 items')

        await user.click(tooltip)

        // Tooltip should remain stable and accessible after click
        expect(tooltip).toBeInTheDocument()
        expect(tooltip).toHaveAttribute('title', '100 items')
        expect(tooltip).toHaveTextContent('100 items')
      })
    })

    describe('Default values and fallbacks', () => {
      it('should not render a label element when label prop is not provided', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={100} />)

        // Verify only the formatted value is rendered, no label
        expect(screen.getByText('100 items')).toBeInTheDocument()

        // Verify no element with label styling exists
        const labelElements = document.querySelectorAll('.text-sm.font-medium')
        expect(labelElements).toHaveLength(0)
      })

      it('should use empty string as default className', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        const { container } = render(<InfoBlock icon={faUser} value={100} />)

        const wrapper = container.firstChild as HTMLElement
        expect(wrapper).toHaveClass('flex')
      })

      it('should use precision 1 as default', () => {
        mockMillify.mockReturnValue('1.2k')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={1234} />)

        expect(mockMillify).toHaveBeenCalledWith(1234, { precision: 1 })
      })
    })

    describe('Text and content rendering', () => {
      it('should render formatted value correctly', () => {
        mockMillify.mockReturnValue('2.5k')
        mockPluralize.mockReturnValue('stars')

        render(<InfoBlock icon={faStar} value={2500} />)

        expect(screen.getByText('2.5k stars')).toBeInTheDocument()
      })

      it('should render label with correct styling', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('repos')

        render(<InfoBlock icon={faCode} value={100} label="Repositories" />)

        const label = screen.getByText('Repositories')
        expect(label).toHaveClass('text-sm', 'font-medium')
      })

      it('should render tooltip content correctly for positive values', () => {
        mockMillify.mockReturnValue('1.5k')
        mockPluralize.mockReturnValue('contributors')

        render(<InfoBlock icon={faUser} value={1500} />)

        const tooltip = screen.getByTestId('tooltip')
        expect(tooltip).toHaveAttribute('title', '1,500 contributors')
      })

      it('should render tooltip content correctly for zero values', () => {
        mockMillify.mockReturnValue('0')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={0} />)

        const tooltip = screen.getByTestId('tooltip')
        expect(tooltip).toHaveAttribute('title', 'No items')
      })
    })

    describe('Handles edge cases and invalid inputs', () => {
      it('should handle value of 0', () => {
        mockMillify.mockReturnValue('0')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={0} />)

        expect(screen.getByText('No items')).toBeInTheDocument()
        expect(screen.getByTestId('tooltip')).toHaveAttribute('title', 'No items')
      })

      it('should handle very large numbers', () => {
        mockMillify.mockReturnValue('1.2B')
        mockPluralize.mockReturnValue('users')

        render(<InfoBlock icon={faUser} value={1234567890} />)

        expect(screen.getByText('1.2B users')).toBeInTheDocument()
        expect(mockMillify).toHaveBeenCalledWith(1234567890, { precision: 1 })
      })

      it('should handle negative numbers (edge case)', () => {
        mockMillify.mockReturnValue('-100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={-100} />)

        expect(screen.getByText('-100 items')).toBeInTheDocument()
      })

      it('should handle decimal precision correctly', () => {
        mockMillify.mockReturnValue('1.234k')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={1234.56} precision={3} />)

        expect(mockMillify).toHaveBeenCalledWith(1234.56, { precision: 3 })
      })

      it('should handle missing optional props gracefully', () => {
        mockMillify.mockReturnValue('42')
        mockPluralize.mockReturnValue('answers')

        render(<InfoBlock icon={faUser} value={42} />)

        expect(screen.getByText('42 answers')).toBeInTheDocument()
        expect(screen.getByTestId('icon-user')).toBeInTheDocument()
        expect(screen.getByTestId('tooltip')).toBeInTheDocument()
      })
    })

    describe('DOM structure / classNames / styles', () => {
      it('should have correct base DOM structure', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        const { container } = render(<InfoBlock icon={faUser} value={100} />)

        const wrapper = container.firstChild as HTMLElement
        expect(wrapper).toHaveClass('flex')

        const icon = screen.getByTestId('icon-user')
        expect(icon).toHaveClass('mr-3', 'mt-1', 'w-5')

        const contentDiv = wrapper.children[1] as HTMLElement
        expect(contentDiv.children[0]).toHaveClass('text-sm', 'md:text-base')
      })

      it('should apply custom className correctly', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        const { container } = render(
          <InfoBlock icon={faUser} value={100} className="custom-class pb-1" />
        )

        const wrapper = container.firstChild as HTMLElement
        expect(wrapper).toHaveClass('flex', 'pb-1', 'custom-class')
      })

      it('should have correct icon styling', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={100} />)

        const icon = screen.getByTestId('icon-user')
        expect(icon).toHaveClass('mr-3', 'mt-1', 'w-5')
      })

      it('should have correct text container styling', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={100} label="Test Label" />)

        const textContainer = screen.getByText('100 items').closest('div')
        expect(textContainer).toHaveClass('text-sm', 'md:text-base')

        const label = screen.getByText('Test Label')
        expect(label).toHaveClass('text-sm', 'font-medium')
      })
    })

    describe('Accessibility and tooltip behavior', () => {
      it('should provide meaningful tooltip content for screen readers', () => {
        mockMillify.mockReturnValue('1.5k')
        mockPluralize.mockReturnValue('contributors')

        render(<InfoBlock icon={faUser} value={1500} />)

        const tooltip = screen.getByTestId('tooltip')
        expect(tooltip).toHaveAttribute('title', '1,500 contributors')
      })

      it('should handle keyboard navigation on tooltip', () => {
        mockMillify.mockReturnValue('100')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={100} />)

        const tooltip = screen.getByTestId('tooltip')

        fireEvent.focus(tooltip)
        fireEvent.blur(tooltip)

        expect(tooltip).toBeInTheDocument()
      })
    })

    describe('Integration with external libraries', () => {
      it('should call millify with correct parameters', () => {
        mockMillify.mockReturnValue('5.67k')
        mockPluralize.mockReturnValue('items')

        render(<InfoBlock icon={faUser} value={5678} precision={2} />)

        expect(mockMillify).toHaveBeenCalledWith(5678, { precision: 2 })
        expect(mockMillify).toHaveBeenCalledTimes(1)
      })

      it('should call pluralize with correct parameters when pluralizedName provided', () => {
        mockMillify.mockReturnValue('3')
        mockPluralize.mockReturnValue('people')

        render(<InfoBlock icon={faUser} value={3} unit="person" pluralizedName="people" />)

        expect(mockPluralize).toHaveBeenCalledWith(3, 'person', 'people')
        expect(mockPluralize).toHaveBeenCalledTimes(1)
      })

      it('should call pluralize with correct parameters when pluralizedName not provided', () => {
        mockMillify.mockReturnValue('3')
        mockPluralize.mockReturnValue('users')

        render(<InfoBlock icon={faUser} value={3} unit="user" />)

        expect(mockPluralize).toHaveBeenCalledWith(3, 'user')
        expect(mockPluralize).toHaveBeenCalledTimes(1)
      })
    })

    describe('Component composition and children handling', () => {
      it('should wrap formatted value in tooltip correctly', () => {
        mockMillify.mockReturnValue('2.5k')
        mockPluralize.mockReturnValue('stars')

        render(<InfoBlock icon={faStar} value={2500} />)

        const tooltip = screen.getByTestId('tooltip')
        expect(tooltip).toContainHTML('2.5k stars')
        expect(tooltip).toHaveAttribute('title', '2,500 stars')
      })
    })
  })

  describe('Performance considerations', () => {
    it('should handle rapid prop changes efficiently', () => {
      mockMillify.mockReturnValue('100')
      mockPluralize.mockReturnValue('items')

      const { rerender } = render(<InfoBlock icon={faUser} value={100} />)

      rerender(<InfoBlock icon={faUser} value={200} />)
      rerender(<InfoBlock icon={faUser} value={300} />)
      rerender(<InfoBlock icon={faUser} value={400} />)

      expect(screen.getByTestId('icon-user')).toBeInTheDocument()
      expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    })
  })
})
