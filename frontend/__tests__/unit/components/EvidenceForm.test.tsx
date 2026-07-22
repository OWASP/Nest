import { screen, fireEvent, waitFor } from '@testing-library/react'
import { useState } from 'react'
import { render } from 'wrappers/testUtil'
import EvidenceForm from 'components/EvidenceForm'

const mockOnSubmit = jest.fn()

const TestWrapper = ({
  initialData,
}: {
  initialData?: { name: string; description: string; sourceUrl: string; file: File | null }
}) => {
  const [formData, setFormData] = useState(
    initialData ?? {
      name: '',
      description: '',
      sourceUrl: '',
      file: null as File | null,
    }
  )

  return (
    <EvidenceForm
      formData={formData}
      setFormData={setFormData}
      onSubmit={mockOnSubmit}
      loading={false}
      title="Add Evidence"
    />
  )
}

describe('EvidenceForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockOnSubmit.mockResolvedValue(undefined)
  })

  describe('file upload (handleFileChange)', () => {
    it('accepts a valid file upload', async () => {
      render(<TestWrapper />)

      const fileInput = screen.getByLabelText(/file/i)
      const file = new File(['dummy content'], 'test.pdf', {
        type: 'application/pdf',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        const nameInput = screen.getByPlaceholderText('Enter evidence name')
        fireEvent.change(nameInput, { target: { value: 'Valid Name' } })
        const descInput = screen.getByPlaceholderText('Enter evidence description')
        fireEvent.change(descInput, { target: { value: 'Valid desc' } })
      })

      const submitButton = screen.getByRole('button', { name: /add evidence/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })

    it('clears file error when file is deselected', async () => {
      render(
        <TestWrapper
          initialData={{
            name: 'Test',
            description: 'Test desc',
            sourceUrl: '',
            file: null,
          }}
        />
      )

      const fileInput = screen.getByLabelText(/file/i)
      const file = new File(['dummy content'], 'test.pdf', {
        type: 'application/pdf',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })
      fireEvent.change(fileInput, { target: { files: [] } })

      const nameInput = screen.getByPlaceholderText('Enter evidence name')
      fireEvent.change(nameInput, { target: { value: 'Valid Name' } })
      const descInput = screen.getByPlaceholderText('Enter evidence description')
      fireEvent.change(descInput, { target: { value: 'Valid desc' } })

      const submitButton = screen.getByRole('button', { name: /add evidence/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Either a file or source URL is required.')).toBeInTheDocument()
      })
    })
  })

  describe('source URL / file validation', () => {
    it('shows error when neither source URL nor file is provided', async () => {
      render(<TestWrapper />)

      const nameInput = screen.getByPlaceholderText('Enter evidence name')
      fireEvent.change(nameInput, { target: { value: 'Valid Name' } })
      const descInput = screen.getByPlaceholderText('Enter evidence description')
      fireEvent.change(descInput, { target: { value: 'Valid description' } })

      const submitButton = screen.getByRole('button', { name: /add evidence/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Either a file or source URL is required.')).toBeInTheDocument()
      })
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('submits when source URL is provided without file', async () => {
      render(<TestWrapper />)

      const nameInput = screen.getByPlaceholderText('Enter evidence name')
      fireEvent.change(nameInput, { target: { value: 'Valid Name' } })
      const descInput = screen.getByPlaceholderText('Enter evidence description')
      fireEvent.change(descInput, { target: { value: 'Valid description' } })
      const urlInput = screen.getByPlaceholderText('https://example.com/document.pdf')
      fireEvent.change(urlInput, { target: { value: 'https://example.com/doc' } })

      const submitButton = screen.getByRole('button', { name: /add evidence/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })
    })
  })

  describe('validation failures', () => {
    it('prevents submission when name is empty', async () => {
      render(<TestWrapper />)

      const submitButton = screen.getByRole('button', { name: /add evidence/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).not.toHaveBeenCalled()
      })
    })
  })

  describe('GraphQL backend errors', () => {
    it('displays and clears backend validation errors on name field', async () => {
      const gqlError = {
        graphQLErrors: [
          { message: 'Name is required', extensions: { code: 'VALIDATION_ERROR', field: 'name' } },
        ],
      }
      mockOnSubmit.mockRejectedValue(gqlError)

      render(<TestWrapper />)

      const nameInput = screen.getByPlaceholderText('Enter evidence name')
      fireEvent.change(nameInput, { target: { value: 'Valid Name' } })
      const descInput = screen.getByPlaceholderText('Enter evidence description')
      fireEvent.change(descInput, { target: { value: 'Valid description' } })
      const urlInput = screen.getByPlaceholderText('https://example.com/document.pdf')
      fireEvent.change(urlInput, { target: { value: 'https://example.com/doc' } })

      const submitButton = screen.getByRole('button', { name: /add evidence/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument()
      })

      fireEvent.change(nameInput, { target: { value: 'Updated Name' } })

      await waitFor(() => {
        expect(screen.queryByText('Name is required')).not.toBeInTheDocument()
      })
    })

    it('clears backend file error when file is changed after validation error', async () => {
      const gqlError = {
        graphQLErrors: [
          { message: 'File is too large', extensions: { code: 'VALIDATION_ERROR', field: 'file' } },
        ],
      }
      mockOnSubmit.mockRejectedValue(gqlError)

      render(<TestWrapper />)

      const nameInput = screen.getByPlaceholderText('Enter evidence name')
      fireEvent.change(nameInput, { target: { value: 'Valid Name' } })
      const descInput = screen.getByPlaceholderText('Enter evidence description')
      fireEvent.change(descInput, { target: { value: 'Valid description' } })
      const urlInput = screen.getByPlaceholderText('https://example.com/document.pdf')
      fireEvent.change(urlInput, { target: { value: 'https://example.com/doc' } })

      const submitButton = screen.getByRole('button', { name: /add evidence/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalled()
      })

      mockOnSubmit.mockResolvedValue(undefined)

      const fileInput = screen.getByLabelText(/file/i)
      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      fireEvent.change(fileInput, { target: { files: [file] } })

      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledTimes(2)
      })
    })
  })
})
