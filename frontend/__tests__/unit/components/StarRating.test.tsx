import { fireEvent, screen } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import StarRating, { MAX_RATING } from 'components/StarRating'

describe('StarRating', () => {
  describe('read-only mode (no onChange)', () => {
    it('renders as a single image with an accessible summary', () => {
      render(<StarRating value={3} />)

      expect(screen.getByRole('img')).toHaveAccessibleName(`Rating: 3 out of ${MAX_RATING} stars`)
    })

    it('uses a custom label when provided', () => {
      render(<StarRating value={4} label="Average rating" />)

      expect(screen.getByRole('img')).toHaveAccessibleName(
        `Average rating: 4 out of ${MAX_RATING} stars`
      )
    })

    it('renders no interactive stars', () => {
      render(<StarRating value={5} />)

      expect(screen.queryByRole('radio')).not.toBeInTheDocument()
      expect(screen.queryByRole('button')).not.toBeInTheDocument()
    })

    it('rounds fractional averages when filling stars', () => {
      const { container } = render(<StarRating value={3.6} />)
      const filled = container.querySelectorAll('.text-yellow-500')

      expect(filled).toHaveLength(4)
    })

    it('fills no stars when unrated', () => {
      const { container } = render(<StarRating value={0} />)

      expect(container.querySelectorAll('.text-yellow-500')).toHaveLength(0)
    })
  })

  describe('interactive mode', () => {
    it('renders one radio per star inside a labelled radio group', () => {
      render(<StarRating value={0} onChange={jest.fn()} label="Your rating" />)

      expect(screen.getAllByRole('radio')).toHaveLength(MAX_RATING)
      expect(screen.getByRole('radiogroup')).toHaveAccessibleName('Your rating')
    })

    it('labels the first star in the singular', () => {
      render(<StarRating value={0} onChange={jest.fn()} />)

      expect(screen.getByRole('radio', { name: '1 star' })).toBeInTheDocument()
      expect(screen.getByRole('radio', { name: '2 stars' })).toBeInTheDocument()
    })

    it('calls onChange with the selected rating', () => {
      const handleChange = jest.fn()
      render(<StarRating value={0} onChange={handleChange} />)

      fireEvent.click(screen.getByRole('radio', { name: '4 stars' }))

      expect(handleChange).toHaveBeenCalledWith(4)
    })

    it('marks only the selected star as checked', () => {
      render(<StarRating value={2} onChange={jest.fn()} />)

      for (const star of [1, 2, 3, 4, 5]) {
        const name = `${star} ${star === 1 ? 'star' : 'stars'}`
        expect(screen.getByRole('radio', { name })).toHaveAttribute(
          'aria-checked',
          String(star === 2)
        )
      }
    })

    it('fills stars up to the current value', () => {
      const { container } = render(<StarRating value={3} onChange={jest.fn()} />)

      expect(container.querySelectorAll('.text-yellow-500')).toHaveLength(3)
    })

    it('previews the hovered rating without committing it', () => {
      const handleChange = jest.fn()
      const { container } = render(<StarRating value={1} onChange={handleChange} />)

      fireEvent.mouseEnter(screen.getByRole('radio', { name: '5 stars' }).parentElement!)

      expect(container.querySelectorAll('.text-yellow-500')).toHaveLength(5)
      expect(handleChange).not.toHaveBeenCalled()
    })

    it('restores the committed rating when the pointer leaves', () => {
      const { container } = render(<StarRating value={1} onChange={jest.fn()} />)
      const star = screen.getByRole('radio', { name: '5 stars' }).parentElement!

      fireEvent.mouseEnter(star)
      fireEvent.mouseLeave(star)

      expect(container.querySelectorAll('.text-yellow-500')).toHaveLength(1)
    })

    it('previews on keyboard focus', () => {
      const { container } = render(<StarRating value={0} onChange={jest.fn()} />)

      fireEvent.focus(screen.getByRole('radio', { name: '3 stars' }))

      expect(container.querySelectorAll('.text-yellow-500')).toHaveLength(3)
    })

    it('does not preview while disabled', () => {
      const { container } = render(<StarRating value={0} onChange={jest.fn()} isDisabled />)

      fireEvent.mouseEnter(screen.getByRole('radio', { name: '5 stars' }).parentElement!)

      expect(container.querySelectorAll('.text-yellow-500')).toHaveLength(0)
    })

    it('disables every star when isDisabled is set', () => {
      const handleChange = jest.fn()
      render(<StarRating value={0} onChange={handleChange} isDisabled />)

      for (const radio of screen.getAllByRole('radio')) {
        expect(radio).toBeDisabled()
      }

      fireEvent.click(screen.getByRole('radio', { name: '3 stars' }))
      expect(handleChange).not.toHaveBeenCalled()
    })

    it.each([
      ['sm', 'h-3.5'],
      ['md', 'h-5'],
      ['lg', 'h-7'],
    ] as const)('applies the %s size class', (size, expectedClass) => {
      const { container } = render(<StarRating value={5} onChange={jest.fn()} size={size} />)

      expect(container.querySelector(`.${CSS.escape(expectedClass)}`)).toBeInTheDocument()
    })
  })
})
