import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SkeletonBase from 'components/SkeletonsBase'

expect.extend(toHaveNoViolations)

const defaultProps = {
  loadingImageUrl: 'https://example.com/loading.gif',
}

describe('SkeletonBase a11y', () => {
  it('should not have any accessibility violations for projects index', async () => {
    const { container } = render(<SkeletonBase {...defaultProps} indexName="projects" />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for users index', async () => {
    const { container } = render(<SkeletonBase indexName="chapters" {...defaultProps} />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for issues index', async () => {
    const { container } = render(<SkeletonBase indexName="issues" {...defaultProps} />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for committees index', async () => {
    const { container } = render(<SkeletonBase indexName="committees" {...defaultProps} />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for organizations index', async () => {
    const { container } = render(<SkeletonBase indexName="organizations" {...defaultProps} />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for snapshots index', async () => {
    const { container } = render(<SkeletonBase indexName="snapshots" {...defaultProps} />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for about index', async () => {
    const { container } = render(<SkeletonBase indexName="about" {...defaultProps} />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for members index', async () => {
    const { container } = render(<SkeletonBase indexName="members" {...defaultProps} />)

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations for organizations-details index', async () => {
    const { container } = render(
      <SkeletonBase indexName="organizations-details" {...defaultProps} />
    )

    const results = await axe(container, {
      rules: {
        'empty-heading': { enabled: false },
      },
    })

    expect(results).toHaveNoViolations()
  })
})
