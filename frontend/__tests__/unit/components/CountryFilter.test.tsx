import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import CountryFilter from 'components/CountryFilter'

describe('<CountryFilter />', () => {
  const defaultProps = {
    countries: ['United States', 'Germany', 'Japan', 'India', 'Indonesia'],
    selectedCountry: '',
    onCountryChange: jest.fn(),
    isLoading: false,
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders with "All Countries" as default input value', () => {
    render(<CountryFilter {...defaultProps} />)
    const input = screen.getByRole('combobox')
    expect(input).toHaveValue('All Countries')
  })

  it('renders country filter with combobox', () => {
    render(<CountryFilter {...defaultProps} />)
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('calls onCountryChange when a country is selected', async () => {
    render(<CountryFilter {...defaultProps} />)

    const input = screen.getByRole('combobox')
    fireEvent.click(input)
    fireEvent.change(input, { target: { value: 'Ger' } })

    await waitFor(() => {
      const option = screen.getByRole('option', { name: 'Germany' })
      fireEvent.click(option)
    })

    fireEvent.click(screen.getByRole('option', { name: 'Germany' }))

    expect(defaultProps.onCountryChange).toHaveBeenCalledWith('Germany')
  })

  it('renders with a selected country as input value', () => {
    render(<CountryFilter {...defaultProps} selectedCountry="Japan" />)
    const input = screen.getByRole('combobox')
    expect(input).toHaveValue('Japan')
  })

  it('renders with empty countries list', () => {
    render(<CountryFilter {...defaultProps} countries={[]} />)
    const input = screen.getByRole('combobox')
    expect(input).toHaveValue('All Countries')
  })

  it('renders with isLoading state', () => {
    render(<CountryFilter {...defaultProps} isLoading={true} />)
    expect(screen.getByRole('combobox')).toBeInTheDocument()
  })

  it('filters options when typing', async () => {
    render(<CountryFilter {...defaultProps} />)

    const input = screen.getByRole('combobox')
    fireEvent.click(input)
    fireEvent.change(input, { target: { value: 'Ind' } })

    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'India' })).toBeInTheDocument()
      expect(screen.getByRole('option', { name: 'Indonesia' })).toBeInTheDocument()
      expect(screen.queryByRole('option', { name: 'Germany' })).not.toBeInTheDocument()
    })
  })
})
