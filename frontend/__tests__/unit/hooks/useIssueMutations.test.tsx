import { useMutation } from '@apollo/client/react'
import { renderHook } from '@testing-library/react'
import { useIssueMutations } from 'hooks/useIssueMutations'
import { GetManagementModuleIssueViewDocument } from 'types/__generated__/issueQueries.generated'

jest.mock('@apollo/client/react', () => ({ useMutation: jest.fn() }))
jest.mock('@heroui/toast', () => ({ addToast: jest.fn() }))

it('refetches the selected issue by its opaque Nest ID after each mutation', () => {
  const mockUseMutation = useMutation as jest.Mock
  mockUseMutation.mockReturnValue([jest.fn(), { loading: false }])
  const issueId = 'SXNzdWVOb2RlOjEyMw=='

  renderHook(() => useIssueMutations({ programKey: 'program', moduleKey: 'module', issueId }))

  expect(mockUseMutation).toHaveBeenCalledTimes(4)
  for (const [, options] of mockUseMutation.mock.calls) {
    expect(options.refetchQueries).toEqual([
      {
        query: GetManagementModuleIssueViewDocument,
        variables: { programKey: 'program', moduleKey: 'module', issueId },
      },
    ])
    expect(options.awaitRefetchQueries).toBe(true)
  }
})
