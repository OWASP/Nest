import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import CountryFilter from 'components/CountryFilter'

const defaultProps = {
  countries: ['United States', 'Germany', 'Japan', 'India', 'Indonesia'],
  selectedCountry: '',
  onCountryChange: jest.fn(),
  isLoading: false,
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('CountryFilter Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
    document.documentElement.classList.toggle('dark', theme === 'dark')
  })

  it('should not have any accessibility violations with default state', async () => {
    const { container } = render(<CountryFilter {...defaultProps} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations with a selected country', async () => {
    const { container } = render(<CountryFilter {...defaultProps} selectedCountry="Japan" />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations when loading', async () => {
    const { container } = render(<CountryFilter {...defaultProps} isLoading={true} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations with empty countries list', async () => {
    const { container } = render(<CountryFilter {...defaultProps} countries={[]} />)

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('should not have any accessibility violations with dropdown open', async () => {
    const { container } = render(<CountryFilter {...defaultProps} />)

    const input = screen.getByRole('combobox')
    fireEvent.click(input)

    await waitFor(() => {
      expect(screen.getByRole('listbox')).toBeInTheDocument()
    })

    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })
})
