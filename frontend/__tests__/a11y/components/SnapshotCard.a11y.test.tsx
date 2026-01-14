import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import SnapshotCard from 'components/SnapshotCard'
expect.extend(toHaveNoViolations)

const defaultProps = {
  key: 'test-snapshot-1',
  title: 'Test Snapshot',
  button: { label: 'Open', onclick: jest.fn() },
  startAt: '2025-01-01T00:00:00Z',
  endAt: '2025-01-10T00:00:00Z',
}

describe('SnapshotCard a11y', () => {
  it('should not have any accessibility violations', async () => {
    const { container } = render(<SnapshotCard {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
