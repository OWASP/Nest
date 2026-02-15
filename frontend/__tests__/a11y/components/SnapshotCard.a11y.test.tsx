import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import SnapshotCard from 'components/SnapshotCard'

const defaultProps = {
  key: 'test-snapshot-1',
  title: 'Test Snapshot',
  button: { label: 'Open', onclick: jest.fn() },
  startAt: 1735689600,
  endAt: 1736467200,
}

describe('SnapshotCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SnapshotCard {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
