import { addToast } from '@heroui/toast'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { render } from 'wrappers/testUtil'
import SponsorApplyPage from 'app/sponsors/apply/page'

jest.mock('@heroui/toast', () => ({
  addToast: jest.fn(),
}))

jest.mock('utils/env.client', () => ({
  API_URL: 'http://localhost:8000/',
}))

const mockFetch = jest.fn()

describe('SponsorApplyPage', () => {
  const mockAddToast = addToast as jest.MockedFunction<typeof addToast>

  beforeEach(() => {
    jest.clearAllMocks()
    globalThis.fetch = mockFetch
  })

  test('renders form fields', () => {
    render(<SponsorApplyPage />)
    expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/website url/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/contact email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/sponsorship interest/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /submit application/i })).toBeInTheDocument()
  })

  test('renders back to sponsors link', () => {
    render(<SponsorApplyPage />)
    expect(screen.getByText('Back to Sponsors')).toBeInTheDocument()
  })

  test('renders cancel link pointing to /sponsors', () => {
    render(<SponsorApplyPage />)
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  test('shows validation error when org name is empty on submit', async () => {
    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'test@example.com' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Organization name is required.')).toBeInTheDocument()
    })
    expect(mockFetch).not.toHaveBeenCalled()
  })

  test('shows validation error when contact email is empty on submit', async () => {
    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'My Org' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Contact email is required.')).toBeInTheDocument()
    })
    expect(mockFetch).not.toHaveBeenCalled()
  })

  test('shows validation error for invalid email format', async () => {
    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'My Org' },
    })
    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'not-an-email' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address.')).toBeInTheDocument()
    })
    expect(mockFetch).not.toHaveBeenCalled()
  })

  test('clears org name error when user types in the field', async () => {
    render(<SponsorApplyPage />)

    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)
    await waitFor(() => {
      expect(screen.getByText('Organization name is required.')).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'Updated Org' },
    })
    await waitFor(() => {
      expect(screen.queryByText('Organization name is required.')).not.toBeInTheDocument()
    })
  })

  test('clears email error when user types in the field', async () => {
    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'My Org' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)
    await waitFor(() => {
      expect(screen.getByText('Contact email is required.')).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'valid@example.com' },
    })
    await waitFor(() => {
      expect(screen.queryByText('Contact email is required.')).not.toBeInTheDocument()
    })
  })

  test('shows success state after successful submission', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true })

    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'Test Org' },
    })
    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'sponsor@example.com' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(screen.getByText('Thank You for Your Interest!')).toBeInTheDocument()
    })
    expect(screen.getByText(/sponsor@example.com/)).toBeInTheDocument()
    expect(mockAddToast).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Application Submitted', color: 'success' })
    )
    expect(screen.getByText('View Sponsors')).toBeInTheDocument()
    expect(screen.getByText('Back to Home')).toBeInTheDocument()
  })

  test('shows error toast when submission returns non-OK response with message', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      headers: { get: jest.fn().mockReturnValue('application/json') },
      json: () => Promise.resolve({ message: 'Duplicate application.' }),
    })

    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'Test Org' },
    })
    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'sponsor@example.com' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Submission Failed', color: 'danger' })
      )
    })
    expect(screen.queryByText('Thank You for Your Interest!')).not.toBeInTheDocument()
  })

  test('shows default error message when non-OK response has no message field', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      headers: { get: jest.fn().mockReturnValue('application/json') },
      json: () => Promise.resolve({}),
    })

    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'Test Org' },
    })
    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'sponsor@example.com' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Failed to submit application. Please try again.',
          color: 'danger',
        })
      )
    })
  })

  test('shows error toast on network error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network failure'))

    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'Test Org' },
    })
    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'sponsor@example.com' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(mockAddToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Error',
          color: 'danger',
        })
      )
    })
  })

  test('updates message field when user types', () => {
    render(<SponsorApplyPage />)
    const messageField = screen.getByLabelText(/sponsorship interest/i)
    fireEvent.change(messageField, {
      target: { name: 'message', value: 'We love open source security!' },
    })
    expect(messageField).toHaveValue('We love open source security!')
  })

  test('calls fetch with correct payload on valid submission', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true })

    render(<SponsorApplyPage />)

    fireEvent.change(screen.getByLabelText(/organization name/i), {
      target: { name: 'organizationName', value: 'ACME Inc' },
    })
    fireEvent.change(screen.getByLabelText(/website url/i), {
      target: { name: 'website', value: 'https://acme.com' },
    })
    fireEvent.change(screen.getByLabelText(/contact email/i), {
      target: { name: 'contactEmail', value: 'info@acme.com' },
    })
    fireEvent.change(screen.getByLabelText(/sponsorship interest/i), {
      target: { name: 'message', value: 'Interested in Gold tier' },
    })
    fireEvent.submit(screen.getByRole('button', { name: /submit application/i }).closest('form')!)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('api/v0/sponsors/apply'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: expect.stringContaining('ACME Inc'),
        })
      )
    })
    const body = JSON.parse(mockFetch.mock.calls[0][1].body)
    expect(body.organization_name).toBe('ACME Inc')
    expect(body.contact_email).toBe('info@acme.com')
    expect(body.website).toBe('https://acme.com')
    expect(body.message).toBe('Interested in Gold tier')
  })
})
