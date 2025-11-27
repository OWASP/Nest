import { render, screen, fireEvent, waitFor } from '@testing-library/react'
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
    className,
  }: React.PropsWithChildren<{
    onPress?: () => void
    'aria-label'?: string
    className?: string
  }>) => (
    <button onClick={onPress} aria-label={ariaLabel} className={className}>
      {children}
    </button>
  ),
}))

jest.mock('@heroui/tooltip', () => ({
  Tooltip: ({ children }: React.PropsWithChildren) => <>{children}</>,
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: ({ icon }: { icon: { iconName: string } }) => (
    <svg data-testid={`icon-${icon.iconName}`} data-icon={icon.iconName} />
  ),
}))

const useThemeMock = useTheme as jest.Mock

describe('ModeToggle Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('should render correctly in light mode and show moon icon', async () => {
    useThemeMock.mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
    })

    render(<ModeToggle />)

    await waitFor(() => {
      const button = screen.getByRole('button', { name: /enable dark mode/i })
      expect(button).toBeInTheDocument()
    })

    const icon = screen.getByTestId('icon-moon')
    expect(icon).toBeInTheDocument()
  })

  test('should render correctly in dark mode and show lightbulb icon', async () => {
    useThemeMock.mockReturnValue({
      theme: 'dark',
      setTheme: jest.fn(),
    })

    render(<ModeToggle />)

    await waitFor(() => {
      const button = screen.getByRole('button', { name: /enable light mode/i })
      expect(button).toBeInTheDocument()
    })

    const icon = screen.getByTestId('icon-lightbulb')
    expect(icon).toBeInTheDocument()
  })

  test('should call setTheme to switch from light to dark when clicked', async () => {
    const setThemeMock = jest.fn()

    useThemeMock.mockReturnValue({
      theme: 'light',
      setTheme: setThemeMock,
    })

    render(<ModeToggle />)

    await waitFor(() => {
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(setThemeMock).toHaveBeenCalledWith('dark')
  })

  test('should call setTheme to switch from dark to light when clicked', async () => {
    const setThemeMock = jest.fn()

    useThemeMock.mockReturnValue({
      theme: 'dark',
      setTheme: setThemeMock,
    })

    render(<ModeToggle />)

    await waitFor(() => {
      expect(screen.getByRole('button')).toBeInTheDocument()
    })

    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(setThemeMock).toHaveBeenCalledWith('light')
  })

  test('should render after mount', () => {
    useThemeMock.mockReturnValue({
      theme: 'light',
      setTheme: jest.fn(),
    })

    const { container } = render(<ModeToggle />)

    // Component is rendered after useEffect runs (which happens synchronously in RTL)
    expect(container.firstChild).not.toBeNull()
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
})
