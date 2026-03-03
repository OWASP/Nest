import { render, screen, fireEvent } from '@testing-library/react'
import { act } from 'react'
import CountryFilter from 'components/CountryFilter'

describe('<CountryFilter />', () => {
  const defaultProps = {
    countries: ['Germany', 'Japan', 'United States'],
    selectedCountry: '',
    onCountryChange: jest.fn(),
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('renders with country label', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} />)
    })
    const sortButton = screen.getByRole('button', { name: /Country/ })
    expect(sortButton).toBeInTheDocument()
  })

  it('renders "All Countries" as default selected value', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} />)
    })
    const selectedValue = screen.getByText('All Countries', { selector: '[data-slot="value"]' })
    expect(selectedValue).toBeInTheDocument()
  })

  it('renders all country options when opened', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} />)
    })
    const sortButton = screen.getByRole('button', { name: /Country/ })
    await act(async () => {
      sortButton.click()
    })
    expect(await screen.findByRole('option', { name: 'All Countries' })).toBeInTheDocument()
    expect(await screen.findByRole('option', { name: 'Germany' })).toBeInTheDocument()
    expect(await screen.findByRole('option', { name: 'Japan' })).toBeInTheDocument()
    expect(await screen.findByRole('option', { name: 'United States' })).toBeInTheDocument()
  })

  it('calls onCountryChange when a country is selected', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} />)
    })
    await act(async () => {
      const hiddenSelect = screen.getByRole('combobox', { hidden: true })
      fireEvent.change(hiddenSelect, { target: { value: 'Japan' } })
    })
    expect(defaultProps.onCountryChange).toHaveBeenCalledWith('Japan')
  })

  it('calls onCountryChange with empty string when "All Countries" is selected', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} selectedCountry="Japan" />)
    })
    await act(async () => {
      const hiddenSelect = screen.getByRole('combobox', { hidden: true })
      fireEvent.change(hiddenSelect, { target: { value: '' } })
    })
    expect(defaultProps.onCountryChange).toHaveBeenCalledWith('')
  })

  it('shows selected country in the trigger', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} selectedCountry="Japan" />)
    })
    const selectedValue = screen.getByText('Japan', { selector: '[data-slot="value"]' })
    expect(selectedValue).toBeInTheDocument()
  })

  it('renders with empty countries list', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} countries={[]} />)
    })
    const sortButton = screen.getByRole('button', { name: /Country/ })
    expect(sortButton).toBeInTheDocument()
  })

  it('has proper accessibility attributes', async () => {
    await act(async () => {
      render(<CountryFilter {...defaultProps} />)
    })
    const hiddenSelect = screen.getByRole('combobox', { hidden: true })
    expect(hiddenSelect.tagName).toBe('SELECT')
    expect(hiddenSelect).toHaveAccessibleName(/Country/)
  })
})
