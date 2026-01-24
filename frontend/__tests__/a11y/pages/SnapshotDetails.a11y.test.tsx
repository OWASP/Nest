import { useQuery } from '@apollo/client/react'
import { mockSnapshotDetailsData } from '@mockData/mockSnapshotData'
import { waitFor, screen } from '@testing-library/react'
import { axe } from 'jest-axe'
import { render } from 'wrappers/testUtil'
import SnapshotDetailsPage from 'app/community/snapshots/[id]/page'

jest.mock('@apollo/client/react', () => ({
  useQuery: jest.fn(),
}))

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(() => ({ push: jest.fn() })),
  useParams: jest.fn(() => ({ id: '2024-12' })),
}))

jest.mock('@/components/MarkdownWrapper', () => {
  return jest.fn(({ content, className }) => (
    <div className={`md-wrapper ${className}`} dangerouslySetInnerHTML={{ __html: content }} />
  ))
})

describe('SnapshotDetails Accessibility', () => {
  it('should have no accessibility violations', async () => {
    ;(useQuery as unknown as jest.Mock).mockReturnValue({
      data: mockSnapshotDetailsData,
      loading: false,
      error: null,
    })

    const { container } = render(<SnapshotDetailsPage />)

    await waitFor(() => {
      expect(screen.getByText('New Snapshot')).toBeInTheDocument()
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
