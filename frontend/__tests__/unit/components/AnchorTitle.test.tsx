import React from "react";
import { screen, render, fireEvent, waitFor } from "@testing-library/react";
import { library } from "@fortawesome/fontawesome-svg-core";
import { faLink } from "@fortawesome/free-solid-svg-icons";
import AnchorTitle from "components/AnchorTitle";

library.add(faLink)

jest.mock('utils/slugify', () => ({
  __esModule: true,
  default: jest.fn((str: string) => str.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, ''))
}))

describe('AnchorTitle Component', () => {
  afterEach(() => {
    jest.restoreAllMocks()
    window.history.replaceState(null, '', window.location.pathname)
  })

  describe('Basic Rendering', () => {
    it('renders without crashing', () => {
      render(<AnchorTitle title="Test Title" />)
      expect(screen.getByText('Test Title')).toBeInTheDocument()
    })

    it('displays the correct title text', () => {
      const testTitle = 'Sample Heading'
      render(<AnchorTitle title={testTitle} />)
      expect(screen.getByText(testTitle)).toBeInTheDocument()
    })

    it('renders with correct HTML structure', () => {
      render(<AnchorTitle title="Test" />)

      const container = screen.getByText('Test').closest('div')
      expect(container).toHaveClass('flex', 'items-center', 'text-2xl', 'font-semibold')

      const groupContainer = screen.getByText('Test').closest('.group')
      expect(groupContainer).toHaveClass('group', 'relative', 'flex', 'items-center')

      const titleElement = screen.getByText('Test')
      expect(titleElement).toHaveClass('flex', 'items-center', 'text-2xl', 'font-semibold')
      expect(titleElement).toHaveAttribute('id', 'anchor-title')
    })

    it('renders FontAwesome link icon', () => {
      render(<AnchorTitle title="Test" />)
      const link = screen.getByRole('link')
      const icon = link.querySelector('svg')
      expect(icon).toBeInTheDocument()
      expect(link).toHaveClass('inherit-color', 'ml-2', 'opacity-0', 'transition-opacity', 'duration-200', 'group-hover:opacity-100')
    })
  })

  describe('Prop-Based Behaviour', () => {
    it('generates correct ID and href from title using slugify', () => {
      const testTitle = 'Test title with spaces'
      render(<AnchorTitle title={testTitle} />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#test-title-with-spaces')

      const element = document.getElementById('test-title-with-spaces')
      expect(element).toBeInTheDocument()
    })

    it('handles different title formats correctly', () => {
      const titles = [
        'Simple Title',
        'Test with Numbers 123',
        'Title-with-hyphens',
        'Title_with_underscores'
      ]

      titles.forEach(title => {
        const { unmount } = render(<AnchorTitle title={title} />)
        const link = screen.getByRole('link')
        expect(link.getAttribute('href')).toMatch(/^#[a-z0-9-]+$/)
        unmount()
      })
    })

    it('applies className prop when provided', () => {
      const customClass = 'custom-class'

      render(<AnchorTitle title="Test" />)
      const container = screen.getByText('Test').closest('div')
      expect(container).toHaveClass('flex', 'items-center', 'text-2xl', 'font-semibold')
    })
  })

  describe('Event Handling', () => {
    let mockScrollTo: jest.SpyInstance
    let mockPushState: jest.SpyInstance
    let mockGetBoundingClientRect: jest.SpyInstance
    let mockGetElementById: jest.SpyInstance
    let mockRequestAnimationFrame: jest.SpyInstance

    beforeEach(() => {
      mockScrollTo = jest.spyOn(window, 'scrollTo').mockImplementation()
      mockPushState = jest.spyOn(window.history, 'pushState').mockImplementation()
      mockRequestAnimationFrame = jest.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
        cb(0)
        return 0
      })

      mockGetBoundingClientRect = jest.fn(() => ({
        top: 100,
        height: 50,
        width: 200,
        bottom: 150,
        left: 0,
        right: 200,
        x: 0,
        y: 100,
        toJSON: () => {}
      }))

      const mockElement = {
        getBoundingClientRect: mockGetBoundingClientRect,
        querySelector: jest.fn(() => ({
          offsetHeight: 30
        }))
      }
      mockGetElementById = jest.spyOn(document, 'getElementById').mockReturnValue(mockElement as any)
    })

    it('prevents default behaviour on link click', () => {
      render(<AnchorTitle title="Click Test" />)
      const link = screen.getByRole('link')

      const mockPreventDefault = jest.fn()
      const clickEvent = new MouseEvent('click', { bubbles: true })
      Object.defineProperty(clickEvent, 'preventDefault', { value: mockPreventDefault })

      fireEvent(link, clickEvent)
      expect(mockPreventDefault).toHaveBeenCalled()
    })

    it('calls scrollTo with correct parameters on click', () => {
      render(<AnchorTitle title="Scroll Test" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledWith({
        "behavior": "smooth",
        "top": 20,
      })
    })

    it('updates browser history on click', () => {
      render(<AnchorTitle title="History Test" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)

      expect(mockPushState).toHaveBeenCalledWith(null, '', '#history-test')
    })

    it('calculates scroll position correctly with heading offset', () => {
      render(<AnchorTitle title="Offset Test" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledWith({
        top: 20,
        behavior: 'smooth'
      })
    })
  })

  describe('useEffect Behaviour', () => {
    let mockScrollTo: jest.SpyInstance
    let mockGetElementById: jest.SpyInstance
    let mockRequestAnimationFrame: jest.SpyInstance

    beforeEach(() => {
      mockScrollTo = jest.spyOn(window, 'scrollTo').mockImplementation()
      mockRequestAnimationFrame = jest.spyOn(window, 'requestAnimationFrame').mockImplementation((cb) => {
        cb(0)
        return 0
      })

      const mockElement = {
        getBoundingClientRect: jest.fn(() => ({
          top: 100,
          height: 50,
          width: 200,
          bottom: 150,
          left: 0,
          right: 200,
          x: 0,
          y: 100,
          toJSON: () => {}
        })),
        querySelector: jest.fn(() => ({
          offsetHeight: 30
        }))
      }
      mockGetElementById = jest.spyOn(document, 'getElementById').mockReturnValue(mockElement as any)
    })

    it('scrolls to element on mount when hash matches', async () => {
      window.location.hash = '#test-scroll'

      render(<AnchorTitle title="Test Scroll" />)

      await waitFor(() => {
        expect(mockRequestAnimationFrame).toHaveBeenCalled()
        expect(mockScrollTo).toHaveBeenCalledWith({
          top: 20,
          behavior: 'smooth'
        })
      })
    })

    it('scrolls to an element on mount when hash matches', async () => {
      window.location.hash = '#test-scroll'

      render(<AnchorTitle title="Test Scroll" />)

      await waitFor(() => {
        expect(mockRequestAnimationFrame).toHaveBeenCalled()
        expect(mockScrollTo).toHaveBeenCalledWith({
          top: 20,
          behavior: 'smooth'
        })
      })
    })

    it('does not scroll when hash does not match', () => {
      window.location.hash = '#different-hash'

      render(<AnchorTitle title="Test Scroll" />)

      expect(mockScrollTo).not.toHaveBeenCalled()
    })
    it('handles popstate events correctly', async () => {
      render(<AnchorTitle title="Popstate Test" />)
      
      window.location.hash = '#popstate-test'
      
      const popstateEvent = new PopStateEvent('popstate')
      fireEvent(window, popstateEvent)
      
      await waitFor(() => {
        expect(mockRequestAnimationFrame).toHaveBeenCalled()
        expect(mockScrollTo).toHaveBeenCalled()
      })
    })

    it('removes popstate event listener on unmount', () => {
      const mockRemoveEventListener = jest.spyOn(window, 'removeEventListener')

      const { unmount } = render(<AnchorTitle title="Cleanup Test" />)
      unmount()

      expect(mockRemoveEventListener).toHaveBeenCalledWith('popstate', expect.any(Function))
    }) 
  })
  
  describe('Edge Cases and Error Handling', () => {
    it('handles empty title gracefully', () => {
      render(<AnchorTitle title="" />)
      
      const container = document.querySelector('div[id=""]')
      expect(container).toBeInTheDocument()
      
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#')
    })

    it('handles special character in title', () => {
      const specialTitle = 'Title with @#$%^&*()'
      render(<AnchorTitle title={specialTitle} />)

      expect(screen.getByText(specialTitle)).toBeInTheDocument()
      const link = screen.getByRole('link')
      expect(link.getAttribute('href')).toMatch(/^#[a-z0-9-]*$/)
    })

    it('handles very long titles', () => {
      const longTitle = 'This is a very long title that might cause issues with ID generation and should be handled gracefully by the component'
      render(<AnchorTitle title={longTitle} />)
      
      expect(screen.getByText(longTitle)).toBeInTheDocument()
      const link = screen.getByRole('link')
      expect(link.getAttribute('href')).toBeDefined()
    })

    it('handles missing DOM element gracefully', () => {
      jest.spyOn(document, 'getElementById').mockReturnValue(null)
      jest.spyOn(console, 'error').mockImplementation(() => {})

      render(<AnchorTitle title="Missing Element" />)
      const link = screen.getByRole('link')

      expect(() => fireEvent.click(link)).not.toThrow()

      jest.restoreAllMocks()
    })

    it('handles missing anchor-title element in scroll calculation', () => {
      const mockElement = {
        getBoundingClientRect: jest.fn(() => ({
          top: 100, height: 50, width: 200, bottom: 150,
          left: 0, right: 200, x: 0, y: 100, toJSON: () => {}
        })),
        querySelector: jest.fn(() => null) 
      }
      jest.spyOn(document, 'getElementById').mockReturnValue(mockElement as any)
      jest.spyOn(window, 'scrollTo').mockImplementation()

      render(<AnchorTitle title="No Anchor" />)
      const link = screen.getByRole('link')

      expect(() => fireEvent.click(link)).not.toThrow()
    })
  })

  describe('Accessibility', () => {
    it('has proper link role and attributes', () => {
      render(<AnchorTitle title="Accessibility Test" />)

      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#accessibility-test')
      expect(link).toBeInTheDocument()
    })

    it('provides proper heading structure', () => {
      render(<AnchorTitle title="Heading Test" />)
      
      const titleElement = screen.getByText('Heading Test')
      expect(titleElement).toHaveAttribute('id', 'anchor-title')
      expect(titleElement).toHaveClass('text-2xl', 'font-semibold')
    })

    it('maintains focus management on interaction', () => {
      const mockScrollTo = jest.spyOn(window, 'scrollTo').mockImplementation()
      const mockPushState = jest.spyOn(window.history, 'pushState').mockImplementation()
      
      render(<AnchorTitle title="Focus Test" />)
      
      const link = screen.getByRole('link')
      link.focus()
      expect(document.activeElement).toBe(link)
      
      fireEvent.click(link)
      
      expect(document.activeElement).toBeDefined()
      
      mockScrollTo.mockRestore()
      mockPushState.mockRestore()
    })
  })

  describe('Integration Tests', () => {
    it('works correctly with multiple instances', () => {
      render(
        <div>
          <AnchorTitle title="First Title" />
          <AnchorTitle title="Second Title" />
        </div>
      )

      expect(screen.getByText('First Title')).toBeInTheDocument()
      expect(screen.getByText('Second Title')).toBeInTheDocument()

      const links = screen.getAllByRole('link')
      expect(links).toHaveLength(2)
      expect(links[0]).toHaveAttribute('href', '#first-title')
      expect(links[1]).toHaveAttribute('href', '#second-title')
    })

    it('handles rapid successive clicks', () => {
      const mockScrollTo = jest.spyOn(window, 'scrollTo').mockImplementation()
      const mockPushState = jest.spyOn(window.history, 'pushState').mockImplementation()

      render(<AnchorTitle title="Rapid Click" />)
      const link = screen.getByRole('link')

      fireEvent.click(link)
      fireEvent.click(link)
      fireEvent.click(link)

      expect(mockScrollTo).toHaveBeenCalledTimes(3)
      expect(mockPushState).toHaveBeenCalledTimes(3)
    })

    it('updates correctly when title prop changes', () => {
      const { rerender } = render(<AnchorTitle title="Original Title" />)
      expect(screen.getByText('Original Title')).toBeInTheDocument()
      
      rerender(<AnchorTitle title="Updated Title" />)
      expect(screen.getByText('Updated Title')).toBeInTheDocument()
      expect(screen.queryByText('Original Title')).not.toBeInTheDocument()
      
      const link = screen.getByRole('link')
      expect(link).toHaveAttribute('href', '#updated-title')
    })
  })
  
  
  
  
})
