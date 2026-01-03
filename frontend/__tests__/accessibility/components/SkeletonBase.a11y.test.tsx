import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SkeletonBase from 'components/SkeletonsBase'

expect.extend(toHaveNoViolations)

const defaultProps = {
  indexName: 'projects',
  loadingImageUrl: 'https://example.com/loading.gif',
}

describe('SkeletonBase a11y =', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SkeletonBase {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
