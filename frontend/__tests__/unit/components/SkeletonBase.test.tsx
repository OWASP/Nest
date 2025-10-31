import { render, screen } from '@testing-library/react'
import React from 'react'
import SkeletonBase from 'components/SkeletonsBase'

jest.mock('@heroui/skeleton', () => ({
  Skeleton: ({ className, children }: { className?: string; children?: React.ReactNode }) => (
    <div data-testid="hero-skeleton" className={className}>
      {children}
    </div>
  ),
}))

jest.mock('components/LoadingSpinner', () => {
  return function MockLoadingSpinner({ imageUrl }: { imageUrl: string }) {
    return <div data-testid="loading-spinner" data-image-url={imageUrl || ''} />
  }
})

jest.mock('components/skeletons/Card', () => {
  return function MockCardSkeleton({
    showLevel = true,
    showIcons = true,
    showLink = true,
    numIcons = 1,
    showContributors = true,
    showSocial = true,
  }: {
    showLevel?: boolean
    showIcons?: boolean
    showLink?: boolean
    numIcons?: number
    showContributors?: boolean
    showSocial?: boolean
  }) {
    return (
      <div
        data-testid="card-skeleton"
        data-show-level={showLevel}
        data-show-icons={showIcons}
        data-show-link={showLink}
        data-num-icons={numIcons}
        data-show-contributors={showContributors}
        data-show-social={showSocial}
      />
    )
  }
})

jest.mock('components/skeletons/UserCard', () => {
  return function MockUserCardSkeleton() {
    return <div data-testid="user-card-skeleton" />
  }
})

describe('SkeletonBase', () => {
  const defaultProps = {
    indexName: 'projects',
    loadingImageUrl: 'https://example.com/loading.gif',
  }

  describe('Basic Rendering', () => {
    it('renders successfully with minimal required props', () => {
      render(<SkeletonBase {...defaultProps} />)
      expect(screen.getAllByTestId('card-skeleton')[0]).toBeInTheDocument()
    })

    it('renders without crashing when props are provided', () => {
      const { container } = render(<SkeletonBase {...defaultProps} />)
      expect(container.firstChild).toBeInTheDocument()
    })

    it('renders different components based on indexName prop', () => {
      const { rerender } = render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)
      expect(screen.getAllByTestId('card-skeleton')).toHaveLength(4)

      rerender(<SkeletonBase indexName="users" loadingImageUrl="test.jpg" />)
      expect(screen.getAllByTestId('user-card-skeleton')).toHaveLength(12)
    })
  })

  describe('Conditional Rendering Logic', () => {
    it('renders LoadingSpinner for unknown indexName', () => {
      render(<SkeletonBase indexName="unknown" loadingImageUrl="test-image.jpg" />)

      const spinner = screen.getByTestId('loading-spinner')
      expect(spinner).toBeInTheDocument()
      expect(spinner).toHaveAttribute('data-image-url', 'test-image.jpg')
    })

    it('renders LoadingSpinner for empty indexName', () => {
      render(<SkeletonBase indexName="" loadingImageUrl="empty.jpg" />)

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    })

    it('renders user cards grid for users indexName', () => {
      render(<SkeletonBase indexName="users" loadingImageUrl="test.jpg" />)

      const userCards = screen.getAllByTestId('user-card-skeleton')
      expect(userCards).toHaveLength(12)

      const gridContainer = userCards[0].parentElement
      expect(gridContainer).toHaveClass(
        'grid',
        'grid-cols-1',
        'gap-6',
        'sm:grid-cols-2',
        'lg:grid-cols-3',
        'xl:grid-cols-4'
      )
    })

    it('renders skeleton components for non-users indexName', () => {
      render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)

      const skeletonComponents = screen.getAllByTestId('card-skeleton')
      expect(skeletonComponents).toHaveLength(4)
    })
  })

  describe('Prop-based Behaviour', () => {
    it('configures chapters skeleton correctly', () => {
      render(<SkeletonBase indexName="chapters" loadingImageUrl="test.jpg" />)

      expect(screen.getByTestId('hero-skeleton')).toBeInTheDocument()
      expect(screen.getByTestId('hero-skeleton')).toHaveClass('mb-2', 'h-96', 'w-full', 'max-w-6xl')

      const cardSkeletons = screen.getAllByTestId('card-skeleton')
      for (const skeleton of cardSkeletons) {
        expect(skeleton).toHaveAttribute('data-show-level', 'false')
        expect(skeleton).toHaveAttribute('data-show-icons', 'false')
        expect(skeleton).toHaveAttribute('data-show-link', 'false')
      }
    })

    it('configures issues skeleton correctly', () => {
      render(<SkeletonBase indexName="issues" loadingImageUrl="test.jpg" />)

      const cardSkeletons = screen.getAllByTestId('card-skeleton')
      for (const skeleton of cardSkeletons) {
        expect(skeleton).toHaveAttribute('data-show-level', 'false')
        expect(skeleton).toHaveAttribute('data-show-icons', 'true')
        expect(skeleton).toHaveAttribute('data-num-icons', '2')
        expect(skeleton).toHaveAttribute('data-show-contributors', 'false')
        expect(skeleton).toHaveAttribute('data-show-social', 'false')
      }
    })

    it('configures projects skeleton correctly', () => {
      render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)

      const cardSkeletons = screen.getAllByTestId('card-skeleton')
      for (const skeleton of cardSkeletons) {
        expect(skeleton).toHaveAttribute('data-show-link', 'false')
        expect(skeleton).toHaveAttribute('data-show-social', 'false')
        expect(skeleton).toHaveAttribute('data-show-icons', 'true')
        expect(skeleton).toHaveAttribute('data-num-icons', '3')
      }
    })

    it('configures committees skeleton correctly', () => {
      render(<SkeletonBase indexName="committees" loadingImageUrl="test.jpg" />)

      const cardSkeletons = screen.getAllByTestId('card-skeleton')
      for (const skeleton of cardSkeletons) {
        expect(skeleton).toHaveAttribute('data-show-link', 'false')
        expect(skeleton).toHaveAttribute('data-show-level', 'false')
        expect(skeleton).toHaveAttribute('data-show-icons', 'true')
        expect(skeleton).toHaveAttribute('data-num-icons', '1')
      }
    })

    it('passes loadingImageUrl to LoadingSpinner correctly', () => {
      const testImageUrl = 'https://example.com/custom-loading.gif'
      render(<SkeletonBase indexName="unknown" loadingImageUrl={testImageUrl} />)

      const spinner = screen.getByTestId('loading-spinner')
      expect(spinner).toHaveAttribute('data-image-url', testImageUrl)
    })
  })

  describe('State Changers / Internal Logic', () => {
    it('switches between different skeleton configurations based on indexName', () => {
      const { rerender } = render(<SkeletonBase indexName="issues" loadingImageUrl="test.jpg" />)

      let cardSkeletons = screen.getAllByTestId('card-skeleton')
      expect(cardSkeletons[0]).toHaveAttribute('data-num-icons', '2')

      rerender(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)
      cardSkeletons = screen.getAllByTestId('card-skeleton')
      expect(cardSkeletons[0]).toHaveAttribute('data-num-icons', '3')

      rerender(<SkeletonBase indexName="committees" loadingImageUrl="test.jpg" />)
      cardSkeletons = screen.getAllByTestId('card-skeleton')
      expect(cardSkeletons[0]).toHaveAttribute('data-num-icons', '1')
    })

    it('correctly determines component type based on switch logic', () => {
      const { unmount: unmountChapters } = render(
        <SkeletonBase indexName="chapters" loadingImageUrl="test.jpg" />
      )
      expect(screen.getAllByTestId('card-skeleton')[0]).toBeInTheDocument()
      unmountChapters()

      const { unmount: unmountIssues } = render(
        <SkeletonBase indexName="issues" loadingImageUrl="test.jpg" />
      )
      expect(screen.getAllByTestId('card-skeleton')[0]).toBeInTheDocument()
      unmountIssues()

      const { unmount: unmountProjects } = render(
        <SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />
      )
      expect(screen.getAllByTestId('card-skeleton')[0]).toBeInTheDocument()
      unmountProjects()

      const { unmount: unmountCommittees } = render(
        <SkeletonBase indexName="committees" loadingImageUrl="test.jpg" />
      )
      expect(screen.getAllByTestId('card-skeleton')[0]).toBeInTheDocument()
      unmountCommittees()

      const { unmount: unmountUsers } = render(
        <SkeletonBase indexName="users" loadingImageUrl="test.jpg" />
      )
      expect(screen.getAllByTestId('user-card-skeleton')).toHaveLength(12)
      unmountUsers()

      const { unmount: unmountUnknown } = render(
        <SkeletonBase indexName="unknown" loadingImageUrl="test.jpg" />
      )
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
      unmountUnknown()
    })
  })

  describe('Default Values and Fallbacks', () => {
    it('falls back to LoadingSpinner for unhandled indexName values', () => {
      const unhandledValues = ['random', 'test', 'invalid', '123', 'null']

      for (const value of unhandledValues) {
        const { container } = render(
          <SkeletonBase indexName={value} loadingImageUrl="fallback.jpg" />
        )

        expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
        container.remove()
      }
    })

    it('handles case-sensitive indexName correctly', () => {
      const { rerender } = render(<SkeletonBase indexName="Users" loadingImageUrl="test.jpg" />)
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

      rerender(<SkeletonBase indexName="users" loadingImageUrl="test.jpg" />)
      expect(screen.getAllByTestId('user-card-skeleton')).toHaveLength(12)
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
    })

    it('uses default CardSkeleton props when not explicitly set', () => {
      render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)

      const cardSkeletons = screen.getAllByTestId('card-skeleton')
      for (const skeleton of cardSkeletons) {
        expect(skeleton).toHaveAttribute('data-show-level', 'true')
        expect(skeleton).toHaveAttribute('data-show-contributors', 'true')
      }
    })
  })

  describe('Text and Content Rendering', () => {
    it('renders correct number of skeleton components', () => {
      const { rerender } = render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)
      expect(screen.getAllByTestId('card-skeleton')).toHaveLength(4)

      rerender(<SkeletonBase indexName="users" loadingImageUrl="test.jpg" />)
      expect(screen.getAllByTestId('user-card-skeleton')).toHaveLength(12)

      expect(screen.queryByTestId('card-skeleton')).not.toBeInTheDocument()
    })

    it('renders hero skeleton only for chapters', () => {
      const { rerender } = render(<SkeletonBase indexName="chapters" loadingImageUrl="test.jpg" />)
      expect(screen.getByTestId('hero-skeleton')).toBeInTheDocument()

      rerender(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)
      expect(screen.queryByTestId('hero-skeleton')).not.toBeInTheDocument()
    })

    it('does not render extra components for non-chapters types', () => {
      render(<SkeletonBase indexName="issues" loadingImageUrl="test.jpg" />)

      expect(screen.queryByTestId('hero-skeleton')).not.toBeInTheDocument()
      expect(screen.getAllByTestId('card-skeleton')).toHaveLength(4)
    })
  })

  describe('Edge Cases and Invalid Inputs', () => {
    it('handles null indexName', () => {
      render(<SkeletonBase indexName={null as never} loadingImageUrl="test.jpg" />)
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    })

    it('handles undefined indexName', () => {
      render(<SkeletonBase indexName={undefined as never} loadingImageUrl="test.jpg" />)
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    })

    it('handles empty string loadingImageUrl', () => {
      render(<SkeletonBase indexName="unknown" loadingImageUrl="" />)

      const spinner = screen.getByTestId('loading-spinner')
      expect(spinner).toHaveAttribute('data-image-url', '')
    })

    it('handles null loadingImageUrl', () => {
      render(<SkeletonBase indexName="unknown" loadingImageUrl={null as never} />)

      const spinner = screen.getByTestId('loading-spinner')
      expect(spinner).toHaveAttribute('data-image-url', '')
    })

    it('handles special characters in indexName', () => {
      const specialNames = ['test-name', 'test_name', 'test.name', 'test name', '!@#$%']

      for (const name of specialNames) {
        const { container } = render(<SkeletonBase indexName={name} loadingImageUrl="test.jpg" />)

        expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
        container.remove()
      }
    })

    it('handles very long indexName strings', () => {
      const longName = 'a'.repeat(1000)
      render(<SkeletonBase indexName={longName} loadingImageUrl="test.jpg" />)

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    })

    it('handles very long loadingImageUrl strings', () => {
      const longUrl = 'https://example.com/' + 'a'.repeat(1000) + '.jpg'
      render(<SkeletonBase indexName="unknown" loadingImageUrl={longUrl} />)

      const spinner = screen.getByTestId('loading-spinner')
      expect(spinner).toHaveAttribute('data-image-url', longUrl)
    })
  })

  describe('Accessibility', () => {
    it('maintains proper component structure for screen readers', () => {
      const { container } = render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)

      const mainContainer = container.querySelector('div')
      expect(mainContainer).toHaveClass(
        'flex',
        'w-full',
        'flex-col',
        'items-center',
        'justify-center'
      )
    })

    it('provides accessible grid structure for users', () => {
      render(<SkeletonBase indexName="users" loadingImageUrl="test.png" />)

      const userCards = screen.getAllByTestId('user-card-skeleton')
      const gridContainer = userCards[0].parentElement

      expect(gridContainer).toHaveClass('grid')
      expect(gridContainer).toHaveAttribute('class')
    })

    it('ensures skeleton components are properly nested', () => {
      render(<SkeletonBase indexName="chapters" loadingImageUrl="test.jpg" />)

      const heroSkeleton = screen.getByTestId('hero-skeleton')
      const cardSkeletons = screen.getAllByTestId('card-skeleton')

      expect(heroSkeleton.parentElement).toHaveClass('flex', 'w-full', 'flex-col')
      for (const skeleton of cardSkeletons) {
        expect(skeleton.parentElement).toHaveClass('flex', 'w-full', 'flex-col')
      }
    })
  })

  describe('DOM Structure / ClassNames / Styles', () => {
    it('applies correct container classes for non-users components', () => {
      const { container } = render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)

      const mainContainer = container.firstChild as HTMLElement
      expect(mainContainer).toHaveClass(
        'flex',
        'w-full',
        'flex-col',
        'items-center',
        'justify-center'
      )
    })

    it('applies correct hero skeleton classes for chapters', () => {
      render(<SkeletonBase indexName="chapters" loadingImageUrl="test.jpg" />)

      const heroSkeleton = screen.getByTestId('hero-skeleton')
      expect(heroSkeleton).toHaveClass('mb-2', 'h-96', 'w-full', 'max-w-6xl')
    })

    it('applies correct grid classes for users', () => {
      render(<SkeletonBase indexName="users" loadingImageUrl="test.jpg" />)

      const userCards = screen.getAllByTestId('user-card-skeleton')
      const gridContainer = userCards[0].parentElement

      expect(gridContainer).toHaveClass(
        'grid',
        'grid-cols-1',
        'gap-6',
        'sm:grid-cols-2',
        'lg:grid-cols-3',
        'xl:grid-cols-4'
      )
    })

    it('maintains consistent DOM structure across different skeleton types', () => {
      const skeletonTypes = ['chapters', 'issues', 'projects', 'committees']

      for (const type of skeletonTypes) {
        const { container } = render(<SkeletonBase indexName={type} loadingImageUrl="test.jpg" />)

        const mainContainer = container.querySelector('div')
        expect(mainContainer).toHaveClass('flex', 'w-full', 'flex-col')

        container.remove()
      }
    })
  })

  describe('Component Integration', () => {
    it('properly integrates with mocked HeroUI Skeleton component', () => {
      render(<SkeletonBase indexName="chapters" loadingImageUrl="test.jpg" />)

      const heroSkeleton = screen.getByTestId('hero-skeleton')
      expect(heroSkeleton).toBeInTheDocument()
      expect(heroSkeleton).toHaveClass('mb-2', 'h-96', 'w-full', 'max-w-6xl')
    })

    it('properly integrates with mocked CardSkeleton component', () => {
      render(<SkeletonBase indexName="projects" loadingImageUrl="test.jpg" />)

      const cardSkeletons = screen.getAllByTestId('card-skeleton')
      expect(cardSkeletons).toHaveLength(4)

      for (const skeleton of cardSkeletons) {
        expect(skeleton).toHaveAttribute('data-show-link', 'false')
        expect(skeleton).toHaveAttribute('data-show-social', 'false')
      }
    })

    it('properly integrates with mocked UserCardSkeleton component', () => {
      render(<SkeletonBase indexName="users" loadingImageUrl="test.jpg" />)

      const userCards = screen.getAllByTestId('user-card-skeleton')
      expect(userCards).toHaveLength(12)
    })

    it('properly integrates with mocked LoadingSpinner component', () => {
      render(<SkeletonBase indexName="unknown" loadingImageUrl="test-spinner.gif" />)

      const spinner = screen.getByTestId('loading-spinner')
      expect(spinner).toHaveAttribute('data-image-url', 'test-spinner.gif')
    })
  })
})
