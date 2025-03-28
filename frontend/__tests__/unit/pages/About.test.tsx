import { mockAboutData } from '@unit/data/mockAboutData'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { render, screen, waitFor } from 'wrappers/testUtil'
import About from 'pages/About'

jest.mock('api/fetchAlgoliaData', () => ({
  fetchAlgoliaData: jest.fn(),
}))

describe('About Page Component', () => {
  beforeEach(() => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({
      hits: [mockAboutData.project],
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders project data after loading', async () => {
    render(<About />)
    await waitFor(() => {
      expect(screen.getByText('About')).toBeInTheDocument()
      expect(screen.getByText('Project history')).toBeInTheDocument()
      expect(screen.getByText('Leaders')).toBeInTheDocument()
      expect(screen.getByText('Roadmap')).toBeInTheDocument()
    })
  })

  test('displays "No data available." when no project data is found', async () => {
    ;(fetchAlgoliaData as jest.Mock).mockResolvedValue({ hits: [] })
    render(<About />)
    await waitFor(() => {
      expect(screen.getByText('No data available.')).toBeInTheDocument()
    })
  })

  test('renders top contributors correctly', async () => {
    render(<About />)
    await waitFor(() => {
      const firstContributor = mockAboutData.project.top_contributors[0]
      expect(screen.getByText(firstContributor.name)).toBeInTheDocument()
      const SecondContributor = mockAboutData.project.top_contributors[1]
      expect(screen.getByText(SecondContributor.name)).toBeInTheDocument()
      const thirdContributor = mockAboutData.project.top_contributors[2]
      expect(screen.getByText(thirdContributor.name)).toBeInTheDocument()
    })
  })
})
