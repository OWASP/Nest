'use client'

import { useLazyQuery, useMutation } from '@apollo/client/react'
import { registerBreadcrumb } from 'contexts/BreadcrumbContext'
import { useParams, useRouter } from 'next/navigation'
import { useCallback, useEffect, useRef, useState } from 'react'
import { FaCircleCheck, FaTriangleExclamation } from 'react-icons/fa6'
import { ErrorDisplay } from 'app/global-error'
import {
  GET_SUBSCRIPTION_NAME_BY_TOKEN,
  UNSUBSCRIBE_BY_TOKEN,
} from 'server/queries/subscriptionQueries'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const UnsubscribePage = () => {
  const { token } = useParams<{ token: string }>()
  const router = useRouter()
  const [status, setStatus] = useState<'loading' | 'confirm' | 'success' | 'error'>('loading')
  const [subscriptionName, setSubscriptionName] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [errorCode, setErrorCode] = useState(500)
  const [isUnsubscribing, setIsUnsubscribing] = useState(false)
  const fetchedToken = useRef<string | null>(null)

  const [fetchSubscription] = useLazyQuery<{
    subscriptionByToken: { name: string } | null
  }>(GET_SUBSCRIPTION_NAME_BY_TOKEN, { fetchPolicy: 'network-only' })

  const [unsubscribe] = useMutation<{
    unsubscribeByToken: { ok: boolean; message: string }
  }>(UNSUBSCRIBE_BY_TOKEN)

  useEffect(() => {
    if (!token || fetchedToken.current === token) return
    fetchedToken.current = token

    setStatus('loading')
    let active = true

    fetchSubscription({ variables: { token } })
      .then(({ data }) => {
        if (!active) return
        if (data?.subscriptionByToken) {
          setSubscriptionName(data.subscriptionByToken.name)
          setStatus('confirm')
        } else {
          setStatus('error')
          setErrorCode(400)
          setErrorMessage('Invalid or expired unsubscribe link.')
        }
      })
      .catch(() => {
        if (!active) return
        setStatus('error')
        setErrorCode(500)
        setErrorMessage('Something went wrong. Please try again later.')
      })

    return () => {
      active = false
    }
  }, [token, fetchSubscription])

  useEffect(() => {
    if (!subscriptionName || !token) return
    return registerBreadcrumb({ title: subscriptionName, path: `/unsubscribe/${token}` })
  }, [subscriptionName, token])

  const handleConfirm = useCallback(() => {
    if (!token || isUnsubscribing) return
    setIsUnsubscribing(true)

    unsubscribe({ variables: { inputData: { token } } })
      .then(({ data }) => {
        if (data?.unsubscribeByToken?.ok) {
          setStatus('success')
        } else {
          setStatus('error')
          setErrorCode(400)
          setErrorMessage(data?.unsubscribeByToken?.message || 'Failed to unsubscribe.')
        }
      })
      .catch(() => {
        setStatus('error')
        setErrorCode(500)
        setErrorMessage('Something went wrong. Please try again later.')
      })
      .finally(() => {
        setIsUnsubscribing(false)
      })
  }, [token, isUnsubscribing, unsubscribe])

  if (status === 'loading') {
    return <LoadingSpinner />
  }

  if (status === 'error') {
    return <ErrorDisplay statusCode={errorCode} title="Unsubscribe Failed" message={errorMessage} />
  }

  if (status === 'confirm') {
    return (
      <div className="mx-auto flex w-full max-w-6xl flex-1 items-center justify-center p-4">
        <SecondaryCard>
          <div className="py-8 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30">
              <FaTriangleExclamation className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <h1 className="text-2xl font-bold text-gray-700 dark:text-gray-200">
              Confirm Unsubscribe
            </h1>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Are you sure you want to unsubscribe from{' '}
              <strong className="text-gray-700 dark:text-gray-200">{subscriptionName}</strong>?
            </p>
            <p className="mt-4 text-xs text-gray-400 dark:text-gray-500">
              You will no longer receive snapshot digest emails for this subscription.
            </p>
            <div className="mt-6 flex justify-center gap-3">
              <ActionButton onClick={() => router.push('/')}>Cancel</ActionButton>
              <ActionButton onClick={handleConfirm} isDisabled={isUnsubscribing}>
                {isUnsubscribing ? 'Unsubscribing...' : 'Confirm Unsubscribe'}
              </ActionButton>
            </div>
          </div>
        </SecondaryCard>
      </div>
    )
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 items-center justify-center p-4">
      <SecondaryCard>
        <div className="py-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
            <FaCircleCheck className="h-6 w-6 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-700 dark:text-gray-200">Unsubscribed</h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            You have been unsubscribed from{' '}
            <strong className="text-gray-700 dark:text-gray-200">{subscriptionName}</strong>.
          </p>
          <p className="mt-4 text-xs text-gray-400 dark:text-gray-500">
            You will no longer receive snapshot digest emails for this subscription.
          </p>
          <div className="mt-6 flex justify-center">
            <ActionButton onClick={() => router.push('/')}>Return To Home</ActionButton>
          </div>
        </div>
      </SecondaryCard>
    </div>
  )
}

export default UnsubscribePage
