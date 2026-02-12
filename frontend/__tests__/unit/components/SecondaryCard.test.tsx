import { render, screen } from '@testing-library/react'
import { FaUser } from 'react-icons/fa6'
import SecondaryCard from 'components/SecondaryCard'

describe('SecondaryCard Component', () => {
  const defaultProps = {
    title: 'Test Title',
    icon: FaUser,
    children: <p>Test children</p>,
    className: 'custom-class',
  }

  describe('Renders successfully with minimal required props', () => {
    it('renders successfully with only a title', () => {
      render(<SecondaryCard title={defaultProps.title} />)
      expect(screen.getByText(defaultProps.title)).toBeInTheDocument()
    })

    it('renders successfully with only children', () => {
      render(<SecondaryCard>{defaultProps.children}</SecondaryCard>)
      expect(screen.getByText('Test children')).toBeInTheDocument()
    })

    it('renders successfully with no props at all', () => {
      const { container } = render(<SecondaryCard />)
      expect(container.querySelector('.mb-8')).toBeInTheDocument()
    })
  })

  describe('Conditional rendering logic', () => {
    it('does not render the h2 title element when title prop is not provided', () => {
      render(<SecondaryCard />)
      const titleElement = screen.queryByRole('heading')
      expect(titleElement).not.toBeInTheDocument()
    })

    it('renders the h2 title element when title prop is provided', () => {
      render(<SecondaryCard title={defaultProps.title} />)
      const titleElement = screen.getByRole('heading', { name: 'Test Title' })
      expect(titleElement).toBeInTheDocument()
    })

    it('does not render the icon when icon prop is not provided', () => {
      const { container } = render(<SecondaryCard title={defaultProps.title} />)
      const iconElement = container.querySelector('svg')
      expect(iconElement).not.toBeInTheDocument()
    })
  })

  describe('Prop-based behavior - different props affect output', () => {
    it('renders a title and an icon when both are provided', () => {
      render(<SecondaryCard title={defaultProps.title} icon={defaultProps.icon} />)
      expect(screen.getByText(defaultProps.title)).toBeInTheDocument()
      expect(document.querySelector('svg.h-5.w-5')).toBeInTheDocument()
    })

    it('renders children content correctly', () => {
      render(<SecondaryCard>{defaultProps.children}</SecondaryCard>)
      expect(screen.getByText('Test children')).toBeInTheDocument()
    })
  })

  describe('Text and content rendering', () => {
    it('displays the correct text for the title', () => {
      const customTitle = 'My Custom Title'
      render(<SecondaryCard title={customTitle} />)
      expect(screen.getByText(customTitle)).toBeInTheDocument()
    })

    it('renders complex children nodes', () => {
      const complexChildren = (
        <div>
          <span>Nested Content</span>
          <button>Click Me</button>
        </div>
      )
      render(<SecondaryCard>{complexChildren}</SecondaryCard>)
      expect(screen.getByText('Nested Content')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Click Me' })).toBeInTheDocument()
    })
  })

  describe('Handles edge cases and invalid inputs', () => {
    it('handles an empty string for the title prop by not rendering the title element', () => {
      render(<SecondaryCard title="" />)
      const titleElement = screen.queryByRole('heading')
      expect(titleElement).not.toBeInTheDocument()
    })

    it('handles null children gracefully by rendering nothing for the children', () => {
      const { container } = render(<SecondaryCard title="Title">{null}</SecondaryCard>)
      const cardElement = container.firstChild
      const titleElement = screen.getByRole('heading', { name: 'Title' })
      expect(titleElement).toBeInTheDocument()
      expect(cardElement.childNodes.length).toBe(1)
    })

    it('renders correctly when called directly as a function (default props)', () => {
      // This covers the default parameter `= {}` in the component signature
      const { container } = render(SecondaryCard())
      expect(container.querySelector('.mb-8')).toBeInTheDocument()
    })
  })

  describe('Accessibility roles and labels', () => {
    it('renders the title within an h2 tag for proper heading structure', () => {
      render(<SecondaryCard title={defaultProps.title} />)
      const heading = screen.getByRole('heading', { level: 2, name: defaultProps.title })
      expect(heading).toBeInTheDocument()
    })
  })

  describe('DOM structure / classNames / styles', () => {
    it('applies the base and custom classNames to the root div', () => {
      const { container } = render(<SecondaryCard className={defaultProps.className} />)
      const cardElement = container.firstChild
      expect(cardElement).toHaveClass(
        'mb-8',
        'rounded-lg',
        'bg-gray-100',
        'p-6',
        'shadow-md',
        'dark:bg-gray-800'
      )
      expect(cardElement).toHaveClass(defaultProps.className)
    })

    it('has the correct classNames for the h2 title element', () => {
      render(<SecondaryCard title={defaultProps.title} />)
      const titleElement = screen.getByText(defaultProps.title)
      expect(titleElement).toHaveClass(
        'mb-4',
        'flex',
        'flex-row',
        'items-center',
        'gap-2',
        'text-2xl',
        'font-semibold'
      )
    })

    it('has the correct className for the icon', () => {
      render(<SecondaryCard title={defaultProps.title} icon={defaultProps.icon} />)
      const iconElement = document.querySelector('svg.h-5.w-5')
      expect(iconElement).toHaveClass('h-5', 'w-5')
    })
  })
})
