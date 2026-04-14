import { render, screen } from '@testing-library/react'
import React from 'react'
import CardDetailsTags from 'components/CardDetailsPage/CardDetailsTags'

// Mock the child components
jest.mock('components/AnchorTitle', () => {
  return function MockAnchorTitle({ title }: { title: string }) {
    return <span data-testid={`anchor-title-${title}`}>{title}</span>
  }
})

jest.mock('components/ToggleableList', () => {
  return function MockToggleableList({
    entityKey,
    label,
    items,
    isDisabled,
  }: {
    entityKey: string
    label: React.ReactNode
    items: string[]
    icon?: React.ComponentType<unknown>
    isDisabled?: boolean
  }) {
    return (
      <div data-testid={`toggleable-list-${entityKey}`} data-disabled={isDisabled}>
        {label}
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    )
  }
})

describe('CardDetailsTags', () => {
  it('should render null when no props provided', () => {
    const { container } = render(<CardDetailsTags entityKey="test" />)
    expect(container.firstChild).toBeNull()
  })

  describe('Languages and Topics', () => {
    it('should render both languages and topics with md:grid-cols-2', () => {
      const { container } = render(
        <CardDetailsTags entityKey="test" languages={['JavaScript']} topics={['Web']} />
      )

      expect(screen.getByTestId('toggleable-list-test-languages')).toBeInTheDocument()
      expect(screen.getByTestId('toggleable-list-test-topics')).toBeInTheDocument()
      expect(container.querySelector('.md\\:grid-cols-2')).toBeInTheDocument()
    })

    it('should render languages only with md:col-span-1', () => {
      const { container } = render(<CardDetailsTags entityKey="test" languages={['JavaScript']} />)

      expect(screen.getByTestId('toggleable-list-test-languages')).toBeInTheDocument()
      expect(container.querySelector('.md\\:col-span-1')).toBeInTheDocument()
    })

    it('should render topics only with md:col-span-1', () => {
      const { container } = render(<CardDetailsTags entityKey="test" topics={['Web']} />)

      expect(screen.getByTestId('toggleable-list-test-topics')).toBeInTheDocument()
      expect(container.querySelector('.md\\:col-span-1')).toBeInTheDocument()
    })
  })

  describe('Tags, Domains, and Labels', () => {
    it('should render tags and domains with md:grid-cols-2', () => {
      const { container } = render(
        <CardDetailsTags entityKey="test" tags={['Bug']} domains={['Security']} />
      )

      expect(screen.getByTestId('toggleable-list-test-tags')).toBeInTheDocument()
      expect(screen.getByTestId('toggleable-list-test-domains')).toBeInTheDocument()
      expect(container.querySelector('.md\\:grid-cols-2')).toBeInTheDocument()
    })

    it('should render tags only with md:col-span-1', () => {
      const { container } = render(<CardDetailsTags entityKey="test" tags={['Bug']} />)

      expect(screen.getByTestId('toggleable-list-test-tags')).toBeInTheDocument()
      expect(container.querySelector('.md\\:col-span-1')).toBeInTheDocument()
    })

    it('should render domains only with md:col-span-1', () => {
      const { container } = render(<CardDetailsTags entityKey="test" domains={['Security']} />)

      expect(screen.getByTestId('toggleable-list-test-domains')).toBeInTheDocument()
      expect(container.querySelector('.md\\:col-span-1')).toBeInTheDocument()
    })

    it('should render labels with isDisabled={true}', () => {
      render(<CardDetailsTags entityKey="test" labels={['Help']} />)

      const labelsList = screen.getByTestId('toggleable-list-test-labels')
      expect(labelsList).toHaveAttribute('data-disabled', 'true')
    })

    it('should render tags and domains with isDisabled={true}', () => {
      render(<CardDetailsTags entityKey="test" tags={['Bug']} domains={['Security']} />)

      const tagsList = screen.getByTestId('toggleable-list-test-tags')
      const domainsList = screen.getByTestId('toggleable-list-test-domains')
      expect(tagsList).toHaveAttribute('data-disabled', 'true')
      expect(domainsList).toHaveAttribute('data-disabled', 'true')
    })

    it('should render all three sections: tags/domains and labels', () => {
      render(
        <CardDetailsTags entityKey="test" tags={['Bug']} domains={['Security']} labels={['Help']} />
      )

      expect(screen.getByTestId('toggleable-list-test-tags')).toBeInTheDocument()
      expect(screen.getByTestId('toggleable-list-test-domains')).toBeInTheDocument()
      expect(screen.getByTestId('toggleable-list-test-labels')).toBeInTheDocument()
    })

    it('should render labels only', () => {
      render(<CardDetailsTags entityKey="test" labels={['Good First Issue']} />)
      expect(screen.getByTestId('toggleable-list-test-labels')).toBeInTheDocument()
    })
  })

  it('should prioritize languages/topics over tags/domains/labels', () => {
    render(
      <CardDetailsTags
        entityKey="test"
        languages={['Python']}
        topics={['ML']}
        tags={['Important']}
        labels={['Help']}
      />
    )

    expect(screen.getByTestId('toggleable-list-test-languages')).toBeInTheDocument()
    expect(screen.getByTestId('toggleable-list-test-topics')).toBeInTheDocument()
    expect(screen.queryByTestId('toggleable-list-test-tags')).not.toBeInTheDocument()
    expect(screen.queryByTestId('toggleable-list-test-labels')).not.toBeInTheDocument()
  })

  it('should use entityKey correctly in toggleable list identifiers', () => {
    render(<CardDetailsTags entityKey="custom-key" tags={['Bug']} />)
    expect(screen.getByTestId('toggleable-list-custom-key-tags')).toBeInTheDocument()
  })
})
