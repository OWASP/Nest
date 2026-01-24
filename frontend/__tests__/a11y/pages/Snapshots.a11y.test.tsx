import { useQuery } from '@apollo/client/react'
import { mockSnapshotData } from '@mockData/mockSnapshotData'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import SnapshotsPage from 'app/community/snapshots/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

describe('Snapshots Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotData,
      loading: false,
      error: null,
    })

    const { container } = render(<SnapshotsPage />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
