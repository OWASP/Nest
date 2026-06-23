import { render, screen, fireEvent } from '@testing-library/react'
import DropdownActions from 'components/DropdownActions'

const mockOnAction = jest.fn()

const defaultOptions = [
  { key: 'edit', label: 'Edit', onAction: mockOnAction },
  { key: 'delete', label: 'Delete', onAction: mockOnAction },
]

describe('DropdownActions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders trigger button with default aria label', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })
    expect(button).toBeInTheDocument()
  })

  it('renders trigger button with custom label', () => {
    render(<DropdownActions options={defaultOptions} label="Custom" />)
    const button = screen.getByRole('button', { name: /custom/i })
    expect(button).toBeInTheDocument()
  })

  it('toggles dropdown open and closed on button click', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })

    fireEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByRole('menu')).toBeInTheDocument()

    fireEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('renders menu items when open', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    expect(screen.getByText('Edit')).toBeInTheDocument()
    expect(screen.getByText('Delete')).toBeInTheDocument()
  })

  it('calls onAction and closes dropdown when menuitem clicked', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })
    fireEvent.click(button)

    fireEvent.click(screen.getByText('Edit'))
    expect(mockOnAction).toHaveBeenCalledTimes(1)
    expect(button).toHaveAttribute('aria-expanded', 'false')
  })

  it('closes on Escape and returns focus to trigger', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })
    fireEvent.click(button)

    const menu = screen.getByRole('menu')
    fireEvent.keyDown(menu, { key: 'Escape' })

    expect(button).toHaveAttribute('aria-expanded', 'false')
    expect(button).toHaveFocus()
  })

  it('navigates down with ArrowDown', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const menu = screen.getByRole('menu')
    fireEvent.keyDown(menu, { key: 'ArrowDown' })

    const items = screen.getAllByRole('menuitem')
    expect(items[1]).toHaveFocus()
  })

  it('navigates up with ArrowUp', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const menu = screen.getByRole('menu')
    fireEvent.keyDown(menu, { key: 'ArrowDown' })
    fireEvent.keyDown(menu, { key: 'ArrowUp' })

    const items = screen.getAllByRole('menuitem')
    expect(items[0]).toHaveFocus()
  })

  it('wraps to last item on ArrowUp from first', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const menu = screen.getByRole('menu')
    fireEvent.keyDown(menu, { key: 'ArrowUp' })

    const items = screen.getAllByRole('menuitem')
    expect(items[items.length - 1]).toHaveFocus()
  })

  it('wraps to first item on ArrowDown from last', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const menu = screen.getByRole('menu')
    const items = screen.getAllByRole('menuitem')
    for (let i = 0; i < items.length; i++) {
      fireEvent.keyDown(menu, { key: 'ArrowDown' })
    }

    expect(items[0]).toHaveFocus()
  })

  it('activates focused item with Enter', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const menu = screen.getByRole('menu')
    fireEvent.keyDown(menu, { key: 'Enter' })

    expect(mockOnAction).toHaveBeenCalled()
  })

  it('activates focused item with Space', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const menu = screen.getByRole('menu')
    fireEvent.keyDown(menu, { key: ' ' })

    expect(mockOnAction).toHaveBeenCalled()
  })

  it('closes dropdown after activating with Enter', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })
    fireEvent.click(button)

    fireEvent.keyDown(screen.getByRole('menu'), { key: 'Enter' })

    expect(button).toHaveAttribute('aria-expanded', 'false')
  })

  it('closes dropdown after activating with Space', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })
    fireEvent.click(button)

    fireEvent.keyDown(screen.getByRole('menu'), { key: ' ' })

    expect(button).toHaveAttribute('aria-expanded', 'false')
  })

  it('closes dropdown when clicking outside', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })
    fireEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')

    fireEvent.mouseDown(document.body)
    expect(button).toHaveAttribute('aria-expanded', 'false')
  })

  it('does not close when clicking inside the dropdown', () => {
    render(<DropdownActions options={defaultOptions} />)
    const button = screen.getByRole('button', { name: /actions menu/i })
    fireEvent.click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')

    fireEvent.mouseDown(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')
  })

  it('cleans up mousedown listener on unmount', () => {
    const spy = jest.spyOn(document, 'removeEventListener')
    const { unmount } = render(<DropdownActions options={defaultOptions} />)
    unmount()

    expect(spy).toHaveBeenCalledWith('mousedown', expect.any(Function))
    spy.mockRestore()
  })

  it('sets tabIndex correctly based on focus', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const items = screen.getAllByRole('menuitem')
    expect(items[0]).toHaveAttribute('tabIndex', '0')
    expect(items[1]).toHaveAttribute('tabIndex', '-1')
  })

  it('renders option with custom className', () => {
    const options = [
      ...defaultOptions,
      { key: 'danger', label: 'Danger', onAction: jest.fn(), className: 'text-red-500' },
    ]
    render(<DropdownActions options={options} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    const items = screen.getAllByRole('menuitem')
    expect(items[items.length - 1]).toHaveClass('text-red-500')
  })

  it('does nothing on unhandled key', () => {
    render(<DropdownActions options={defaultOptions} />)
    fireEvent.click(screen.getByRole('button', { name: /actions menu/i }))

    fireEvent.keyDown(screen.getByRole('menu'), { key: 'a' })
    expect(screen.getByRole('menu')).toBeInTheDocument()
  })
})
