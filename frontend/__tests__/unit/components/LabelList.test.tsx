import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { LabelList } from 'components/LabelList'

describe('LabelList', () => {
  it('renders nothing when labels are empty', () => {
    const { container } = render(<LabelList entityKey="test-1" labels={[]} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders nothing when labels are undefined', () => {
    const { container } = render(<LabelList entityKey="test-2" labels={undefined} />)
    expect(container).toBeEmptyDOMElement()
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
    expect(screen.queryByText(/\+.*more/)).not.toBeInTheDocument()
  })
})
