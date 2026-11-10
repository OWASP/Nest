import { fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { LabelList } from 'components/LabelList'

describe('LabelList', () => {
  it('renders placeholder when labels are empty', () => {
    render(<LabelList entityKey="test-1" labels={[]} />)
    expect(screen.getByText('No labels assigned')).toBeInTheDocument()
  })

  it('renders placeholder when labels are undefined', () => {
    render(<LabelList entityKey="test-2" labels={undefined} />)
    expect(screen.getByText('No labels assigned')).toBeInTheDocument()
  })

  it('renders labels correctly', () => {
    render(<LabelList entityKey="test-3" labels={['label1', 'label2']} />)
    expect(screen.getByText('label1')).toBeInTheDocument()
    expect(screen.getByText('label2')).toBeInTheDocument()
  })

  it('renders max visible labels and remaining count', () => {
    render(<LabelList entityKey="test-4" labels={['1', '2', '3', '4', '5', '6']} maxVisible={5} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.queryByText('6')).not.toBeInTheDocument()
    expect(screen.getByText('+1 more')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <LabelList entityKey="test-5" labels={['label']} className="custom-class" />
    )
    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('renders all labels when maxVisible is greater than labels length', () => {
    render(<LabelList entityKey="test-6" labels={['1', '2']} maxVisible={5} />)
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.queryByText(/\+\d+ more/)).not.toBeInTheDocument()
  })

  it('renders labels as buttons when onLabelClick is provided', () => {
    render(<LabelList entityKey="test-7" labels={['label1']} onLabelClick={jest.fn()} />)
    expect(screen.getByRole('button', { name: 'Search for label1' })).toBeInTheDocument()
  })

  it('renders labels as text when onLabelClick is not provided', () => {
    render(<LabelList entityKey="test-8" labels={['label1']} />)
    expect(screen.queryByRole('button', { name: 'Search for label1' })).not.toBeInTheDocument()
    expect(screen.getByText('label1')).toBeInTheDocument()
  })

  it('calls onLabelClick with the clicked label', () => {
    const handleLabelClick = jest.fn()
    render(
      <LabelList entityKey="test-9" labels={['label1', 'label2']} onLabelClick={handleLabelClick} />
    )
    fireEvent.click(screen.getByRole('button', { name: 'Search for label1' }))
    expect(handleLabelClick).toHaveBeenCalledWith('label1')
  })

  it('does not render the overflow label as a button', () => {
    render(
      <LabelList
        entityKey="test-10"
        labels={['1', '2', '3', '4', '5', '6']}
        onLabelClick={jest.fn()}
      />
    )
    expect(screen.getByText('+1 more')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Search for +1 more' })).not.toBeInTheDocument()
  })
})
