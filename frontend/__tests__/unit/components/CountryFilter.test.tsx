import { fireEvent, render, screen } from '@testing-library/react'
import { act } from 'react'
import CountryFilter from 'components/CountryFilter'

describe('<CountryFilter />', () => {
  const defaultProps = {
    countries: ['United States', 'Germany', 'Japan'],
    selectedCountry: '',
    onCountryChange: jest.fn(),
    isLoading: false,
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders with "All Countries" selected by default', () => {
    render(<CountryFilter {...defaultProps} />)
    const value = screen.getByText('All Countries', { selector: '[data-slot="value"]' })
    expect(value).toBeInTheDocument()
  })

  it('renders country label', () => {
    render(<CountryFilter {...defaultProps} />)
    const label = screen.getByText('Country :', { selector: '[data-slot="label"]' })
    expect(label).toBeInTheDocument()
  })

  it('calls onCountryChange when a country is selected', async () => {
    render(<CountryFilter {...defaultProps} />)

    await act(async () => {
      const hiddenSelect = document.querySelector(
        '[data-testid="hidden-select-container"] select'
      )
      if (hiddenSelect) {
        fireEvent.change(hiddenSelect, { target: { value: 'Germany' } })
      }
    })

    expect(defaultProps.onCountryChange).toHaveBeenCalledWith('Germany')
  })

  it('renders with a selected country', () => {
    render(<CountryFilter {...defaultProps} selectedCountry="Japan" />)
    const value = screen.getByText('Japan', { selector: '[data-slot="value"]' })
    expect(value).toBeInTheDocument()
  })

  it('renders with empty countries list', () => {
    render(<CountryFilter {...defaultProps} countries={[]} />)
    const value = screen.getByText('All Countries', { selector: '[data-slot="value"]' })
    expect(value).toBeInTheDocument()
  })

  it('renders with isLoading state', () => {
    render(<CountryFilter {...defaultProps} isLoading={true} />)
    const label = screen.getByText('Country :', { selector: '[data-slot="label"]' })
    expect(label).toBeInTheDocument()
  })

  it('renders the trigger button', () => {
    render(<CountryFilter {...defaultProps} />)
    const trigger = screen.getByRole('button', { name: /Country/ })
    expect(trigger).toBeInTheDocument()
  })
})
