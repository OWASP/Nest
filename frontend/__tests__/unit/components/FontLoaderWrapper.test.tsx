import { act, render, screen, waitFor } from '@testing-library/react'
import FontLoaderWrapper from 'components/FontLoaderWrapper'

jest.mock('components/LoadingSpinner', () => {
  return function MockLoadingSpinner() {
    return <div data-testid="loading-spinner">Loading fonts...</div>
  }
})

describe('<FontLoaderWrapper />', () => {
  const originalFonts = document.fonts
  let fontsReadyResolve: (() => void) | null = null

  beforeEach(() => {
    const fontsReadyPromise = new Promise<void>((resolve) => {
      fontsReadyResolve = resolve
    })

    Object.defineProperty(document, 'fonts', {
      value: {
        ready: fontsReadyPromise,
      },
      configurable: true,
    })
  })

  afterEach(() => {
    Object.defineProperty(document, 'fonts', {
      value: originalFonts,
      configurable: true,
    })
    jest.clearAllMocks()
    fontsReadyResolve = null
  })

  async function resolveFontsReady(): Promise<void> {
    await act(async () => {
      fontsReadyResolve?.()
      await document.fonts.ready
    })
  }

  it('renders LoadingSpinner initially while fonts are loading', () => {
    render(
      <FontLoaderWrapper>
        <div>Content</div>
      </FontLoaderWrapper>
    )

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    expect(screen.queryByText('Content')).not.toBeInTheDocument()
  })

  it('renders children after fonts are loaded', async () => {
    render(
      <FontLoaderWrapper>
        <div>Dashboard Content</div>
      </FontLoaderWrapper>
    )

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.getByText('Dashboard Content')).toBeInTheDocument()
    })
  })

  it('hides LoadingSpinner when fonts are loaded', async () => {
    render(
      <FontLoaderWrapper>
        <div>Content</div>
      </FontLoaderWrapper>
    )

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
    })
  })

  it('renders multiple children correctly', async () => {
    render(
      <FontLoaderWrapper>
        <div>Child 1</div>
        <div>Child 2</div>
        <div>Child 3</div>
      </FontLoaderWrapper>
    )

    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.getByText('Child 1')).toBeInTheDocument()
      expect(screen.getByText('Child 2')).toBeInTheDocument()
      expect(screen.getByText('Child 3')).toBeInTheDocument()
    })
  })

  it('updates children when data prop changes', async () => {
    const { rerender } = render(
      <FontLoaderWrapper>
        <div>Initial Content</div>
      </FontLoaderWrapper>
    )

    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.getByText('Initial Content')).toBeInTheDocument()
    })

    rerender(
      <FontLoaderWrapper>
        <div>Updated Content</div>
      </FontLoaderWrapper>
    )

    expect(screen.getByText('Updated Content')).toBeInTheDocument()
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
  })

  it('maintains fontsLoaded state after rerender', async () => {
    const { rerender } = render(
      <FontLoaderWrapper>
        <div>Content 1</div>
      </FontLoaderWrapper>
    )

    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.getByText('Content 1')).toBeInTheDocument()
    })

    rerender(
      <FontLoaderWrapper>
        <div>Content 2</div>
      </FontLoaderWrapper>
    )

    expect(screen.getByText('Content 2')).toBeInTheDocument()
    expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
  })

  it('renders children after fonts promise resolves', async () => {
    render(
      <FontLoaderWrapper>
        <div>Content</div>
      </FontLoaderWrapper>
    )

    // Component calls .then() on document.fonts.ready and renders content once resolved
    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.getByText('Content')).toBeInTheDocument()
    })
  })

  it('handles empty children', async () => {
    render(
      <FontLoaderWrapper>
        <></>
      </FontLoaderWrapper>
    )

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()

    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
    })
  })

  it('renders children as fragment without extra wrapper', async () => {
    render(
      <FontLoaderWrapper>
        <h1>Title</h1>
        <p>Paragraph</p>
      </FontLoaderWrapper>
    )

    await resolveFontsReady()

    await waitFor(() => {
      expect(screen.getByText('Title')).toBeInTheDocument()
      expect(screen.getByText('Paragraph')).toBeInTheDocument()

      const h1 = screen.getByText('Title') as HTMLElement
      const p = screen.getByText('Paragraph') as HTMLElement

      expect(h1.tagName).toBe('H1')
      expect(p.tagName).toBe('P')
    })
  })

  it('does not obscure interactive elements after fonts load', async () => {
    render(
      <FontLoaderWrapper>
        <button>Click me</button>
      </FontLoaderWrapper>
    )

    await resolveFontsReady()

    await waitFor(() => {
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument()
    })
  })
})
