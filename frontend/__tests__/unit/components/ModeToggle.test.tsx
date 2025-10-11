import { render, screen, fireEvent } from '@testing-library/react'
import { useTheme } from 'next-themes'
import React from 'react'
import ModeToggle from 'components/ModeToggle'

jest.mock('next-themes', () => ({
  useTheme: jest.fn(),
}))

jest.mock('@heroui/button', () => ({
  Button: ({
    children,
    onPress,
    'aria-label': ariaLabel,
  }: React.PropsWithChildren<{ onPress?: () => void; 'aria-label'?: string }>) => (
    <button onClick={onPress} aria-label={ariaLabel}>
      {children}
    </button>
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: React.PropsWithChildren) => <>{children}</>,
}))

const useThemeMock = useTheme as jest.Mock

describe('ModeToggle Component', () => {
  test('should render correctly in light mode and show moon icon', () => {
    useThemeMock.mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
    })

    render(<ModeToggle />)

    const button = screen.getByRole('button', { name: /enable dark mode/i })
    expect(button).toBeInTheDocument()

    const icon = document.querySelector('[data-icon="moon"]')
    expect(icon).toBeInTheDocument()
  })

  test('should render correctly in dark mode and show sun icon', () => {
    useThemeMock.mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    })

    render(<ModeToggle />)

    const button = screen.getByRole('button', { name: /enable light mode/i })
    expect(button).toBeInTheDocument()

    const icon = document.querySelector('[data-icon="sun"]')
    expect(icon).toBeInTheDocument()
  })

  test('should call setTheme to switch from light to dark when clicked', () => {
    const setThemeMock = jest.fn()

    useThemeMock.mockReturnValue({
      theme: 'light',
      setTheme: setThemeMock,
    })

    render(<ModeToggle />)
    const button = screen.getByRole('button')

    fireEvent.click(button)

    expect(setThemeMock).toHaveBeenCalledWith('dark')
  })

  test('should call setTheme to switch from dark to light when clicked', () => {
    const setThemeMock = jest.fn()

    useThemeMock.mockReturnValue({
      theme: 'dark',
      setTheme: setThemeMock,
    })

    render(<ModeToggle />)
    const button = screen.getByRole('button')

    fireEvent.click(button)

    expect(setThemeMock).toHaveBeenCalledWith('light')
  })
})
