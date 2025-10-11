import { screen } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import '@testing-library/jest-dom'
import SponsorCard from 'components/SponsorCard'

describe('Sponsor Card tests', () => {
  const defaultProps = {
    target: 'test-target',
    title: 'Test Title',
    type: 'project',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })
  afterEach(() => {
    jest.clearAllMocks()
    jest.restoreAllMocks()
  })

  test.each(['project', 'chapter', 'repository'])('renders SponsorCard with type %s', (type) => {
    render(<SponsorCard {...defaultProps} type={type} />)
    expect(screen.getByText('Want to become a sponsor?')).toBeInTheDocument()
    expect(
      screen.getByText('Support Test Title to help grow global cybersecurity community.')
    ).toBeInTheDocument()
    expect(screen.getByText('Sponsor Test Title')).toBeInTheDocument()
  })

  test.each(['project', 'chapter', 'repository'])(
    'Sponsor card has correct link for type %s',
    (type) => {
      render(<SponsorCard {...defaultProps} type={type} />)
      const link = screen.getByRole('link', { name: /Sponsor Test Title/i })
      expect(link).toHaveAttribute(
        'href',
        `https://owasp.org/donate/?reponame=www-${type}-test-target&title=Test%20Title`
      )
    }
  )
})
