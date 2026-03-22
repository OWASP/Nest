import { render, screen } from '@testing-library/react'
import CardSkeleton from 'components/skeletons/Card'

jest.mock('@heroui/skeleton', () => ({
  Skeleton: ({ className }: { className?: string }) => (
    <div data-testid="skeleton" className={className} />
  ),
}))

describe('CardSkeleton', () => {
  it('renders with default props', () => {
    render(<CardSkeleton />)
    expect(screen.getAllByTestId('skeleton').length).toBeGreaterThan(0)
  })

  it('renders with all props explicitly set to false', () => {
    render(
      <CardSkeleton
        showLevel={false}
        showIcons={false}
        showProjectName={false}
        showSummary={false}
        showLink={false}
        showContributors={false}
        showSocial={false}
        showActionButton={false}
      />
    )
    expect(screen.queryByTestId('skeleton')).not.toBeInTheDocument()
  })

  it('renders with showIcons=false specifically', () => {
    render(<CardSkeleton showIcons={false} />)
    const skeletons = screen.getAllByTestId('skeleton')
    const iconSkeletons = skeletons.filter((s) => s.className?.includes('h-8 w-16'))
    expect(iconSkeletons.length).toBe(0)
  })

  it('renders with custom numIcons', () => {
    const numIcons = 5
    render(<CardSkeleton numIcons={numIcons} />)
    const skeletons = screen.getAllByTestId('skeleton')
    const iconSkeletons = skeletons.filter((s) => s.className?.includes('h-8 w-16'))
    expect(iconSkeletons.length).toBe(numIcons)
  })
})
