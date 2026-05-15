import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CountryFilter from 'components/CountryFilter'

jest.mock('@heroui/autocomplete', () => ({
  Autocomplete: ({
    onSelectionChange,
  }: {
    onSelectionChange?: (key: React.Key | null) => void
  }) => (
    <div>
      <button type="button" aria-label="Simulate null selection" onClick={() => onSelectionChange?.(null)}>
        null
      </button>
      <button
        type="button"
        aria-label="Simulate __all__ key"
        onClick={() => onSelectionChange?.('__all__')}
      >
        all
      </button>
    </div>
  ),
  AutocompleteItem: ({ children }: { children: React.ReactNode }) => <span>{children}</span>,
}))

describe('CountryFilter selection guards', () => {
  it('does not call onCountryChange when selection key is null', async () => {
    const user = userEvent.setup()
    const onCountryChange = jest.fn()
    render(
      <CountryFilter
        countries={['France']}
        selectedCountry=""
        onCountryChange={onCountryChange}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Simulate null selection' }))
    expect(onCountryChange).not.toHaveBeenCalled()
  })

  it('maps __all__ selection key to empty country', async () => {
    const user = userEvent.setup()
    const onCountryChange = jest.fn()
    render(
      <CountryFilter
        countries={['France']}
        selectedCountry="France"
        onCountryChange={onCountryChange}
      />
    )

    await user.click(screen.getByRole('button', { name: 'Simulate __all__ key' }))
    expect(onCountryChange).toHaveBeenCalledWith('')
  })
})
