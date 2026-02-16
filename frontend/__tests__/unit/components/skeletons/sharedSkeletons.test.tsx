import { render, screen } from '@testing-library/react'
import {
  ItemCardSkeleton,
  SectionSkeleton,
  PageWrapper,
  TitleSection,
  TwoColumnSection,
  SectionHeader,
  CardSection,
} from 'components/skeletons/sharedSkeletons'

jest.mock('@heroui/skeleton', () => ({
  Skeleton: ({ className, ...props }: { className?: string; [key: string]: unknown }) => (
    <div data-testid="skeleton" className={className} {...props} />
  ),
}))

describe('sharedSkeletons', () => {
  describe('ItemCardSkeleton', () => {
    it('renders with correct title width', () => {
      render(<ItemCardSkeleton titleWidth="w-1/2" />)
      const skeletons = screen.getAllByTestId('skeleton')
      expect(skeletons[0]).toHaveClass('w-1/2')
    })

    it('renders correct structure', () => {
      render(<ItemCardSkeleton titleWidth="w-1/3" />)
      const skeletons = screen.getAllByTestId('skeleton')
      expect(skeletons).toHaveLength(5)
    })
  })

  describe('SectionSkeleton', () => {
    it('renders correct number of items', () => {
      render(
        <SectionSkeleton
          titleWidth="w-full"
          itemCount={3}
          itemKeyPrefix="test-item"
          titleSkeletonWidth="w-32"
        />
      )
      const skeletons = screen.getAllByTestId('skeleton')
      expect(skeletons).toHaveLength(17)
    })

    it('applies minHeight class', () => {
      const { container } = render(
        <SectionSkeleton
          titleWidth="w-full"
          itemCount={1}
          itemKeyPrefix="test"
          titleSkeletonWidth="w-20"
          minHeight="min-h-[200px]"
        />
      )
      expect(container.firstChild).toHaveClass('min-h-[200px]')
    })
  })

  describe('PageWrapper', () => {
    it('renders children', () => {
      render(
        <PageWrapper>
          <div data-testid="child">Child Content</div>
        </PageWrapper>
      )
      expect(screen.getByTestId('child')).toBeInTheDocument()
    })

    it('sets aria-busy attribute', () => {
      const { container } = render(
        <PageWrapper ariaBusy={false}>
          <div>Child</div>
        </PageWrapper>
      )
      expect(container.firstChild).toHaveAttribute('aria-busy', 'false')
    })

    it('defaults aria-busy to true', () => {
      const { container } = render(
        <PageWrapper>
          <div>Child</div>
        </PageWrapper>
      )
      expect(container.firstChild).toHaveAttribute('aria-busy', 'true')
    })
  })

  describe('TitleSection', () => {
    it('renders with default class name', () => {
      render(<TitleSection />)
      const skeleton = screen.getByTestId('skeleton')
      expect(skeleton).toHaveClass('h-10 w-64 rounded')
    })

    it('renders with custom class name', () => {
      render(<TitleSection skeletonClassName="h-12 w-full" />)
      const skeleton = screen.getByTestId('skeleton')
      expect(skeleton).toHaveClass('h-12 w-full')
    })
  })

  describe('TwoColumnSection', () => {
    it('renders multiple sections', () => {
      const sections = [
        { keyPrefix: 's1', titleWidth: 'w-20', itemTitleWidth: 'w-full' },
        { keyPrefix: 's2', titleWidth: 'w-30', itemTitleWidth: 'w-half' },
      ]
      render(<TwoColumnSection sections={sections} />)
      const skeletons = screen.getAllByTestId('skeleton')
      expect(skeletons).toHaveLength(54)
    })
  })

  describe('SectionHeader', () => {
    it('renders with rounded class when true', () => {
      render(<SectionHeader titleSkeletonWidth="w-20" rounded={true} />)
      const skeletons = screen.getAllByTestId('skeleton')
      expect(skeletons[0]).toHaveClass('rounded')
      expect(skeletons[1]).toHaveClass('rounded')
    })

    it('renders without rounded class when false', () => {
      render(<SectionHeader titleSkeletonWidth="w-20" rounded={false} />)
      const skeletons = screen.getAllByTestId('skeleton')
      expect(skeletons[0]).not.toHaveClass('rounded', { exact: false })
    })

    it('renders correct title width', () => {
      render(<SectionHeader titleSkeletonWidth="w-40" />)
      const skeletons = screen.getAllByTestId('skeleton')
      expect(skeletons[1]).toHaveClass('w-40')
    })
  })

  describe('CardSection', () => {
    it('renders children', () => {
      render(
        <CardSection>
          <div data-testid="card-child">Content</div>
        </CardSection>
      )
      expect(screen.getByTestId('card-child')).toBeInTheDocument()
    })

    it('applies custom classes, minHeight, and colSpan', () => {
      const { container } = render(
        <CardSection className="custom-class" minHeight="min-h-10" colSpan="col-span-2">
          <div>Content</div>
        </CardSection>
      )
      expect(container.firstChild).toHaveClass('custom-class')
      expect(container.firstChild).toHaveClass('min-h-10')
      expect(container.firstChild).toHaveClass('col-span-2')
    })
  })
})
