import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import EntityActions from 'components/EntityActions'

// Mock next/navigation
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

describe('EntityActions', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  describe('Program Actions - Create Module', () => {
    it('navigates to create module page when Add Module is clicked', () => {
      render(<EntityActions type="program" programKey="test-program" />)
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const addModuleButton = screen.getByText('Add Module')
      fireEvent.click(addModuleButton)

      expect(mockPush).toHaveBeenCalledWith('/my/mentorship/programs/test-program/modules/create')
    })

    it('closes dropdown after clicking Add Module', () => {
      render(<EntityActions type="program" programKey="test-program" />)
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      const addModuleButton = screen.getByText('Add Module')
      fireEvent.click(addModuleButton)

      expect(button).toHaveAttribute('aria-expanded', 'false')
    })
  })

  describe('Module Actions - Edit Module', () => {
    it('navigates to edit module page when Edit is clicked with moduleKey', () => {
      render(<EntityActions type="module" programKey="test-program" moduleKey="test-module" />)
      const button = screen.getByRole('button', { name: /Module actions menu/ })
      fireEvent.click(button)

      const editButton = screen.getByText('Edit')
      fireEvent.click(editButton)

      expect(mockPush).toHaveBeenCalledWith(
        '/my/mentorship/programs/test-program/modules/test-module/edit'
      )
    })

    it('does not navigate when moduleKey is missing for edit action', () => {
      render(<EntityActions type="module" programKey="test-program" />)
      const button = screen.getByRole('button', { name: /Module actions menu/ })
      fireEvent.click(button)

      const editButton = screen.getByText('Edit')
      fireEvent.click(editButton)

      expect(mockPush).not.toHaveBeenCalled()
    })

    it('closes dropdown after clicking Edit', () => {
      render(<EntityActions type="module" programKey="test-program" moduleKey="test-module" />)
      const button = screen.getByRole('button', { name: /Module actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      const editButton = screen.getByText('Edit')
      fireEvent.click(editButton)

      expect(button).toHaveAttribute('aria-expanded', 'false')
    })
  })

  describe('Module Actions - View Issues', () => {
    it('navigates to view issues page when View Issues is clicked with moduleKey', () => {
      render(<EntityActions type="module" programKey="test-program" moduleKey="test-module" />)
      const button = screen.getByRole('button', { name: /Module actions menu/ })
      fireEvent.click(button)

      const viewIssuesButton = screen.getByText('View Issues')
      fireEvent.click(viewIssuesButton)

      expect(mockPush).toHaveBeenCalledWith(
        '/my/mentorship/programs/test-program/modules/test-module/issues'
      )
    })

    it('does not navigate when moduleKey is missing for view issues action', () => {
      render(<EntityActions type="module" programKey="test-program" />)
      const button = screen.getByRole('button', { name: /Module actions menu/ })
      fireEvent.click(button)

      const viewIssuesButton = screen.getByText('View Issues')
      fireEvent.click(viewIssuesButton)

      expect(mockPush).not.toHaveBeenCalled()
    })

    it('closes dropdown after clicking View Issues', () => {
      render(<EntityActions type="module" programKey="test-program" moduleKey="test-module" />)
      const button = screen.getByRole('button', { name: /Module actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      const viewIssuesButton = screen.getByText('View Issues')
      fireEvent.click(viewIssuesButton)

      expect(button).toHaveAttribute('aria-expanded', 'false')
    })
  })

  describe('Program Status Changes - Publish', () => {
    it('calls setStatus with PUBLISHED when Publish is clicked', () => {
      const mockSetStatus = jest.fn()
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Draft}
          setStatus={mockSetStatus}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const publishButton = screen.getByText('Publish')
      fireEvent.click(publishButton)

      expect(mockSetStatus).toHaveBeenCalledWith(ProgramStatusEnum.Published)
    })

    it('shows Publish option only when status is DRAFT', () => {
      render(
        <EntityActions type="program" programKey="test-program" status={ProgramStatusEnum.Draft} />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.getByText('Publish')).toBeInTheDocument()
    })

    it('does not show Publish option when status is PUBLISHED', () => {
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.queryByText('Publish')).not.toBeInTheDocument()
    })

    it('closes dropdown after clicking Publish', () => {
      const mockSetStatus = jest.fn()
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Draft}
          setStatus={mockSetStatus}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      const publishButton = screen.getByText('Publish')
      fireEvent.click(publishButton)

      expect(button).toHaveAttribute('aria-expanded', 'false')
    })
  })

  describe('Program Status Changes - Draft (Unpublish)', () => {
    it('calls setStatus with DRAFT when Unpublish is clicked from PUBLISHED', () => {
      const mockSetStatus = jest.fn()
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
          setStatus={mockSetStatus}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const unpublishButton = screen.getByText('Unpublish')
      fireEvent.click(unpublishButton)

      expect(mockSetStatus).toHaveBeenCalledWith(ProgramStatusEnum.Draft)
    })

    it('calls setStatus with DRAFT when Unpublish is clicked from COMPLETED', () => {
      const mockSetStatus = jest.fn()
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Completed}
          setStatus={mockSetStatus}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const unpublishButton = screen.getByText('Unpublish')
      fireEvent.click(unpublishButton)

      expect(mockSetStatus).toHaveBeenCalledWith(ProgramStatusEnum.Draft)
    })

    it('shows Unpublish option when status is PUBLISHED', () => {
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.getByText('Unpublish')).toBeInTheDocument()
    })

    it('shows Unpublish option when status is COMPLETED', () => {
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Completed}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.getByText('Unpublish')).toBeInTheDocument()
    })

    it('does not show Unpublish option when status is DRAFT', () => {
      render(
        <EntityActions type="program" programKey="test-program" status={ProgramStatusEnum.Draft} />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.queryByText('Unpublish')).not.toBeInTheDocument()
    })

    it('closes dropdown after clicking Unpublish', () => {
      const mockSetStatus = jest.fn()
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
          setStatus={mockSetStatus}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      const unpublishButton = screen.getByText('Unpublish')
      fireEvent.click(unpublishButton)

      expect(button).toHaveAttribute('aria-expanded', 'false')
    })
  })

  describe('Program Status Changes - Completed', () => {
    it('calls setStatus with COMPLETED when Mark as Completed is clicked', () => {
      const mockSetStatus = jest.fn()
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
          setStatus={mockSetStatus}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const completedButton = screen.getByText('Mark as Completed')
      fireEvent.click(completedButton)

      expect(mockSetStatus).toHaveBeenCalledWith(ProgramStatusEnum.Completed)
    })

    it('shows Mark as Completed option only when status is PUBLISHED', () => {
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.getByText('Mark as Completed')).toBeInTheDocument()
    })

    it('does not show Mark as Completed when status is DRAFT', () => {
      render(
        <EntityActions type="program" programKey="test-program" status={ProgramStatusEnum.Draft} />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.queryByText('Mark as Completed')).not.toBeInTheDocument()
    })

    it('does not show Mark as Completed when status is COMPLETED', () => {
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Completed}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(screen.queryByText('Mark as Completed')).not.toBeInTheDocument()
    })

    it('closes dropdown after clicking Mark as Completed', () => {
      const mockSetStatus = jest.fn()
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
          setStatus={mockSetStatus}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      const completedButton = screen.getByText('Mark as Completed')
      fireEvent.click(completedButton)

      expect(button).toHaveAttribute('aria-expanded', 'false')
    })
  })

  describe('Click Outside Behavior', () => {
    it('closes dropdown when clicking outside', async () => {
      render(<EntityActions type="program" programKey="test-program" />)
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      fireEvent.mouseDown(document.body)

      await waitFor(() => {
        expect(button).toHaveAttribute('aria-expanded', 'false')
      })
    })

    it('does not close dropdown when clicking inside', () => {
      render(<EntityActions type="program" programKey="test-program" />)
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)
      expect(button).toHaveAttribute('aria-expanded', 'true')

      fireEvent.mouseDown(button)

      expect(button).toHaveAttribute('aria-expanded', 'true')
    })

    it('cleans up event listener on unmount', () => {
      const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener')
      const { unmount } = render(<EntityActions type="program" programKey="test-program" />)

      unmount()

      expect(removeEventListenerSpy.mock.calls).toEqual(
        expect.arrayContaining([['mousedown', expect.any(Function)]])
      )
      removeEventListenerSpy.mockRestore()
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('handles undefined setStatus gracefully when clicking Publish', () => {
      render(
        <EntityActions type="program" programKey="test-program" status={ProgramStatusEnum.Draft} />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const publishButton = screen.getByText('Publish')
      // Should not throw error even without setStatus
      expect(() => fireEvent.click(publishButton)).not.toThrow()
    })

    it('handles undefined setStatus gracefully when clicking Unpublish', () => {
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const unpublishButton = screen.getByText('Unpublish')
      expect(() => fireEvent.click(unpublishButton)).not.toThrow()
    })

    it('handles undefined setStatus gracefully when clicking Mark as Completed', () => {
      render(
        <EntityActions
          type="program"
          programKey="test-program"
          status={ProgramStatusEnum.Published}
        />
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const completedButton = screen.getByText('Mark as Completed')
      expect(() => fireEvent.click(completedButton)).not.toThrow()
    })

    it('handles undefined status gracefully', () => {
      render(<EntityActions type="program" programKey="test-program" />)
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      // Should still show Edit and Add Module
      expect(screen.getByText('Edit')).toBeInTheDocument()
      expect(screen.getByText('Add Module')).toBeInTheDocument()
    })
  })

  describe('Event Propagation', () => {
    it('prevents event propagation on button click', () => {
      const mockParentClick = jest.fn()
      render(
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
        <div onClick={mockParentClick}>
          <EntityActions type="program" programKey="test-program" />
        </div>
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      expect(mockParentClick).not.toHaveBeenCalled()
    })

    it('prevents event propagation on menu item click', () => {
      const mockParentClick = jest.fn()
      render(
        // eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
        <div onClick={mockParentClick}>
          <EntityActions type="program" programKey="test-program" />
        </div>
      )
      const button = screen.getByRole('button', { name: /Program actions menu/ })
      fireEvent.click(button)

      const editButton = screen.getByText('Edit')
      fireEvent.click(editButton)

      expect(mockParentClick).not.toHaveBeenCalled()
    })
  })
})
