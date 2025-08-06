import { render, fireEvent, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import ProgramActions from 'components/ProgramActions'

const push = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push }),
}))

describe('ProgramActions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders the Select Action button', () => {
    render(<ProgramActions isDraft={false} />)
    expect(screen.getByText('Select Action')).toBeInTheDocument()
  })

  it('shows Publish Program option if isDraft is true', () => {
    render(<ProgramActions isDraft={true} />)
    fireEvent.click(screen.getByText('Select Action'))
    expect(screen.getByText('Publish Program')).toBeInTheDocument()
  })

  it('does not show Publish Program option if isDraft is false', () => {
    render(<ProgramActions isDraft={false} />)
    fireEvent.click(screen.getByText('Select Action'))
    expect(screen.queryByText('Publish Program')).not.toBeInTheDocument()
  })

  it('calls setPublish when Publish Program is clicked', () => {
    const setPublish = jest.fn()
    render(<ProgramActions isDraft={true} setPublish={setPublish} />)
    fireEvent.click(screen.getByText('Select Action'))
    fireEvent.click(screen.getByText('Publish Program'))
    expect(setPublish).toHaveBeenCalled()
  })

  it('navigates to create module page when Add Module is clicked', () => {
    render(<ProgramActions isDraft={false} />)
    fireEvent.click(screen.getByText('Select Action'))
    fireEvent.click(screen.getByText('Add Module'))
    expect(push).toHaveBeenCalledWith(`${window.location.pathname}/modules/create`)
  })

  it('has correct menuitem roles for accessibility', () => {
    render(<ProgramActions isDraft={true} />)
    fireEvent.click(screen.getByText('Select Action'))
    const menuItems = screen.getAllByRole('menuitem')
    expect(menuItems.length).toBe(2)
    expect(menuItems[0]).toHaveTextContent('Add Module')
    expect(menuItems[1]).toHaveTextContent('Publish Program')
  })
})
