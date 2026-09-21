'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useDjangoSession } from 'hooks/useDjangoSession'
import { signIn } from 'next-auth/react'
import { useEffect, useState } from 'react'
import { FaStar } from 'react-icons/fa6'
import {
  DeleteSnapshotFeedbackDocument,
  GetSnapshotFeedbackDocument,
  SubmitSnapshotFeedbackDocument,
} from 'types/__generated__/snapshotQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import ActionButton from 'components/ActionButton'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { AuthorAvatar } from 'components/ItemCardList'
import SecondaryCard from 'components/SecondaryCard'
import StarRating, { MAX_RATING } from 'components/StarRating'

export const MAX_COMMENT_LENGTH = 1000

type SnapshotFeedbackProps = {
  snapshotKey: string
}

const SnapshotFeedback = ({ snapshotKey }: SnapshotFeedbackProps) => {
  const { isSyncing, status } = useDjangoSession()
  const isAuthenticated = status === 'authenticated'

  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState('')

  const { data, refetch } = useQuery(GetSnapshotFeedbackDocument, {
    variables: { key: snapshotKey },
    fetchPolicy: 'cache-and-network',
    errorPolicy: 'all',
    skip: isSyncing,
  })

  const snapshot = data?.snapshot
  const myFeedback = snapshot?.myFeedback ?? null
  const entries = snapshot?.feedback ?? []
  const hasExistingFeedback = myFeedback != null
  const averageRating = snapshot?.averageRating ?? 0
  const feedbackCount = snapshot?.feedbackCount ?? 0
  useEffect(() => {
    setRating(myFeedback?.rating ?? 0)
    setComment(myFeedback?.comment ?? '')
  }, [myFeedback?.rating, myFeedback?.comment])

  const [submitFeedback, { loading: isSubmitting }] = useMutation(SubmitSnapshotFeedbackDocument, {
    onCompleted: (result) => {
      const { ok, message } = result.submitSnapshotFeedback
      addToast({
        title: ok ? 'Thank you!' : 'Error',
        description: message,
        color: ok ? 'success' : 'danger',
      })
      if (ok) refetch()
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to submit your feedback.',
        color: 'danger',
      })
    },
  })

  const [deleteFeedback, { loading: isDeleting }] = useMutation(DeleteSnapshotFeedbackDocument, {
    onCompleted: (result) => {
      const { ok, message } = result.deleteSnapshotFeedback
      addToast({
        title: ok ? 'Removed' : 'Error',
        description: message,
        color: ok ? 'success' : 'danger',
      })
      if (ok) {
        setRating(0)
        setComment('')
        refetch()
      }
    },
    onError: () => {
      addToast({
        title: 'Error',
        description: 'Failed to remove your feedback.',
        color: 'danger',
      })
    },
  })

  const isBusy = isSubmitting || isDeleting

  const handleSubmit = () => {
    if (rating < 1) {
      addToast({
        title: 'Rating required',
        description: 'Please select a star rating before submitting.',
        color: 'warning',
      })
      return
    }

    submitFeedback({ variables: { inputData: { snapshotKey, rating, comment } } })
  }

  const renderSummary = () => {
    if (feedbackCount === 0) {
      return (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No ratings yet. Be the first to share your thoughts.
        </p>
      )
    }

    return (
      <>
        <StarRating value={averageRating} label="Average rating" />
        <span className="text-lg font-semibold text-gray-700 dark:text-gray-200">
          {averageRating.toFixed(1)}
          <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
            {' '}
            / {MAX_RATING}
          </span>
        </span>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          ({feedbackCount} {feedbackCount === 1 ? 'rating' : 'ratings'})
        </span>
      </>
    )
  }

  const renderForm = () => {
    if (!isAuthenticated) {
      return (
        <div className="mb-6 rounded-lg border border-dashed border-gray-300 p-4 text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">
          <button
            type="button"
            onClick={() => signIn('github')}
            className="cursor-pointer bg-transparent text-[#1D7BD7] hover:underline"
          >
            Sign in
          </button>{' '}
          to rate this snapshot and leave a comment.
        </div>
      )
    }

    return (
      <div className="mb-6 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
        <h3 className="mb-3 text-sm font-semibold text-gray-600 dark:text-gray-300">
          {hasExistingFeedback ? 'Update your feedback' : 'Rate this snapshot'}
        </h3>

        <StarRating
          isDisabled={isBusy}
          label="Your rating"
          onChange={setRating}
          size="lg"
          value={rating}
        />

        <div className="mt-4">
          <FormTextarea
            disabled={isBusy}
            id="snapshot-feedback-comment"
            label="Comment"
            maxLength={MAX_COMMENT_LENGTH}
            onChange={(e) => setComment(e.target.value)}
            placeholder="What did you find most useful in this snapshot?"
            rows={3}
            value={comment}
          />
          <div className="mt-1 text-right text-xs text-gray-400">
            {comment.length}/{MAX_COMMENT_LENGTH}
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-3">
          <ActionButton isDisabled={isBusy} onClick={handleSubmit}>
            {isSubmitting && 'Saving...'}
            {!isSubmitting && (hasExistingFeedback ? 'Update Feedback' : 'Submit Feedback')}
          </ActionButton>
          {hasExistingFeedback && (
            <ActionButton
              isDisabled={isBusy}
              onClick={() => deleteFeedback({ variables: { snapshotKey } })}
            >
              {isDeleting ? 'Removing...' : 'Remove'}
            </ActionButton>
          )}
        </div>
      </div>
    )
  }

  return (
    <SecondaryCard icon={FaStar} title="Community Feedback">
      <div className="mb-6 flex flex-wrap items-center gap-3">{renderSummary()}</div>

      {renderForm()}

      {entries.length > 0 && (
        <div className="flex flex-col gap-4">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
              data-testid="snapshot-feedback-entry"
            >
              <div className="flex w-full items-center">
                <AuthorAvatar
                  author={{
                    avatarUrl: entry.avatarUrl,
                    login: entry.login,
                    name: entry.username,
                  }}
                />
                <span className="min-w-0 font-semibold">{entry.username}</span>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <StarRating label={`Rating by ${entry.username}`} size="sm" value={entry.rating} />
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {formatDate(entry.createdAt)}
                </span>
              </div>
              {entry.comment && (
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{entry.comment}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </SecondaryCard>
  )
}

export default SnapshotFeedback
