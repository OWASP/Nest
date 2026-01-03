import { render } from '@testing-library/react'
import { mockProjectDetailsData } from '@unit/data/mockProjectDetailsData'
import { axe, toHaveNoViolations } from 'jest-axe'
import Leaders from 'components/Leaders'

expect.extend(toHaveNoViolations)

jest.mock('next/image', () => ({
  __esModule: true,
  default: ({
    src,
    alt,
    width,
    height,
    className,
  }: {
    src: string
    alt: string
    width: number
    height: number
    className?: string
  }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={className}
      data-testid="avatar-image"
    />
  ),
}))

describe('Leaders a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<Leaders users={mockProjectDetailsData.project.entityLeaders} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
