/// <reference types="jest" />
import { screen, fireEvent } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import '@testing-library/jest-dom'
import SponsorTierSection from 'components/sponsors/SponsorTierSection'
import { SponsorData } from 'types/sponsor'

const mockSponsors: SponsorData[] = [
  {
    id: '1',
    name: 'Zebra Corp',
    imageUrl: '/img1.jpg',
    sponsorType: 'Corporate',
    url: 'https://zebra.com',
  },
  {
    id: '2',
    name: 'Apple Inc',
    imageUrl: '/img2.jpg',
    sponsorType: 'Corporate',
    url: 'https://apple.com',
  },
  {
    id: '3',
    name: 'Banana Tech',
    imageUrl: '/img3.jpg',
    sponsorType: 'Corporate',
    url: 'https://banana.com',
  },
  {
    id: '4',
    name: 'Cherry Digital',
    imageUrl: '/img4.jpg',
    sponsorType: 'Corporate',
    url: 'https://cherry.com',
  },
  {
    id: '5',
    name: 'Date Systems',
    imageUrl: '/img5.jpg',
    sponsorType: 'Corporate',
    url: 'https://date.com',
  },
  {
    id: '6',
    name: 'Elderberry Ltd',
    imageUrl: '/img6.jpg',
    sponsorType: 'Corporate',
    url: 'https://elderberry.com',
  },
  {
    id: '7',
    name: 'Fig Network',
    imageUrl: '/img7.jpg',
    sponsorType: 'Corporate',
    url: 'https://fig.com',
  },
  {
    id: '8',
    name: 'Grape Global',
    imageUrl: '/img8.jpg',
    sponsorType: 'Corporate',
    url: 'https://grape.com',
  },
  {
    id: '9',
    name: 'Honeydew LLC',
    imageUrl: '/img9.jpg',
    sponsorType: 'Corporate',
    url: 'https://honeydew.com',
  },
]

describe('SponsorTierSection tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('returns null when sponsors array is empty', () => {
    const { container } = render(<SponsorTierSection tier="diamond" sponsors={[]} />)
    expect(container.querySelector('section')).not.toBeInTheDocument()
  })

  test('renders all sponsors and sorts alphabetically for non-supporter tier', () => {
    render(<SponsorTierSection tier="diamond" sponsors={mockSponsors.slice(0, 3)} />)

    expect(screen.getByText('Diamond')).toBeInTheDocument()
    expect(screen.getByText('Diamond sponsors')).toBeInTheDocument()

    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0]).toHaveAttribute('aria-label', 'Apple Inc (opens in new tab)')
    expect(links[1]).toHaveAttribute('aria-label', 'Banana Tech (opens in new tab)')
    expect(links[2]).toHaveAttribute('aria-label', 'Zebra Corp (opens in new tab)')
  })

  test('renders all items even for > 8 items if tier is not supporter', () => {
    render(<SponsorTierSection tier="silver" sponsors={mockSponsors} />)

    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(9)

    expect(screen.queryByRole('button', { name: /Show More/i })).not.toBeInTheDocument()
  })

  test('applies MaxItems logic for supporter tier with > 8 items, showing Expand/Collapse toggle', () => {
    render(<SponsorTierSection tier="supporter" sponsors={mockSponsors} />)

    let links = screen.getAllByRole('link')
    expect(links).toHaveLength(8)

    const toggleButton = screen.getByRole('button', { name: /Show More/i })
    expect(toggleButton).toBeInTheDocument()

    fireEvent.click(toggleButton)

    links = screen.getAllByRole('link')
    expect(links).toHaveLength(9)

    expect(screen.getByRole('button', { name: /Show Less/i })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /Show Less/i }))

    links = screen.getAllByRole('link')
    expect(links).toHaveLength(8)
    expect(screen.getByRole('button', { name: /Show More/i })).toBeInTheDocument()
  })

  test('does not show expand button for supporter tier with <= 8 items', () => {
    render(<SponsorTierSection tier="supporter" sponsors={mockSponsors.slice(0, 8)} />)

    const links = screen.getAllByRole('link')
    expect(links).toHaveLength(8)

    expect(screen.queryByRole('button', { name: /Show More/i })).not.toBeInTheDocument()
  })
})
