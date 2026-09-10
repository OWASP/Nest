'use client'

import { useMutation } from '@apollo/client/react'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'
import { FaCircleCheck } from 'react-icons/fa6'

import { ErrorDisplay } from 'app/global-error'
import { UNSUBSCRIBE_BY_TOKEN } from 'server/queries/subscriptionQueries'
import ActionButton from 'components/ActionButton'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const UnsubscribePage = () => {
  const { token } = useParams<{ token: string }>()
  const router = useRouter()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const [errorCode, setErrorCode] = useState(500)
  const hasRun = useRef(false)

  const [unsubscribe] = useMutation<{
    unsubscribeByToken: { ok: boolean; message: string }
  }>(UNSUBSCRIBE_BY_TOKEN)

  useEffect(() => {
    if (!token || hasRun.current) return
    hasRun.current = true

    unsubscribe({ variables: { token } })
      .then(({ data }) => {
        if (data?.unsubscribeByToken?.ok) {
          setStatus('success')
          setMessage('You have been successfully unsubscribed.')
        } else {
          setStatus('error')
          setErrorCode(400)
          setMessage(data?.unsubscribeByToken?.message || 'Failed to unsubscribe.')
        }
      })
      .catch(() => {
        setStatus('error')
        setErrorCode(500)
        setMessage('Something went wrong. Please try again later.')
      })
  }, [token, unsubscribe])

  if (status === 'loading') {
    return <LoadingSpinner />
  }

  if (status === 'error') {
    return <ErrorDisplay statusCode={errorCode} title="Unsubscribe Failed" message={message} />
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 items-center justify-center p-4">
      <SecondaryCard>
        <div className="py-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
            <FaCircleCheck className="h-6 w-6 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-2xl font-bold text-gray-700 dark:text-gray-200">Unsubscribed</h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{message}</p>
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
