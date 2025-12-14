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

jest.mock('react-icons/md', () => ({
  MdLightMode: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="md-light-mode-icon" data-icon="light" {...props} />
  ),
  MdDarkMode: (props: React.SVGProps<SVGSVGElement>) => (
    <svg data-testid="md-dark-mode-icon" data-icon="dark" {...props} />
  ),
}))

const useThemeMock = useTheme as jest.Mock

describe('ModeToggle Component', () => {
  test('should render correctly in light mode and show dark mode icon', () => {
    useThemeMock.mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
    })

    render(<ModeToggle />)

    const button = screen.getByRole('button', { name: /enable dark mode/i })
    expect(button).toBeInTheDocument()

    const icon = screen.getByTestId('md-dark-mode-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('data-icon', 'dark')
  })

  test('should render correctly in dark mode and show light mode icon', () => {
    useThemeMock.mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    })

    render(<ModeToggle />)

    const button = screen.getByRole('button', { name: /enable light mode/i })
    expect(button).toBeInTheDocument()

    const icon = screen.getByTestId('md-light-mode-icon')
    expect(icon).toBeInTheDocument()
    expect(icon).toHaveAttribute('data-icon', 'light')
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
