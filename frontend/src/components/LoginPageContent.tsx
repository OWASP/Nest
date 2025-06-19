'use client'

import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useSession, signIn } from 'next-auth/react'
import { FC, useCallback, useEffect } from 'react'
import { userAuthStatus } from 'utils/constants'

type LoginPageContentProps = {
  readonly isGitHubAuthEnabled: boolean
}

const LoginPageContent: FC<LoginPageContentProps> = ({ isGitHubAuthEnabled }) => {
  const { status } = useSession()
  const router = useRouter()
  const handleRedirect = useCallback(() => {
    addToast({
      description: 'You are already logged in.',
      title: 'Already logged in',
      timeout: 3000,
      shouldShowTimeoutProgress: true,
      color: 'default',
      variant: 'solid',
    })
    router.push('/')
  }, [router])

  useEffect(() => {
    if (status === userAuthStatus.AUTHENTICATED) {
      handleRedirect()
    }
  }, [status, handleRedirect])

  if (!isGitHubAuthEnabled) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center">
        <span className="text-lg text-gray-500">Signing In with GitHub is not enabled.</span>
      </div>
    )
  }

  if (status === userAuthStatus.LOADING) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center gap-2">
        <FontAwesomeIcon icon={faSpinner} spin height={16} width={16} />
        <span className="text-lg text-gray-500">Checking session...</span>
      </div>
    )
  }

  if (status === userAuthStatus.AUTHENTICATED) {
    return (
      <div className="flex min-h-[80vh] items-center justify-center gap-2">
        <FontAwesomeIcon icon={faSpinner} spin height={16} width={16} />
        <span className="text-lg text-gray-500">Redirecting...</span>
      </div>
    )
  }

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <div className="w-full max-w-sm space-y-6 rounded-2xl border border-gray-200 bg-owasp-blue p-8 shadow-xl dark:border-slate-700 dark:bg-slate-800">
        <h2 className="text-center text-2xl font-bold text-gray-900 dark:text-white">
          Welcome back
        </h2>
        <p className="text-center text-sm text-gray-500 dark:text-gray-400">
          Sign in with your GitHub account to continue
        </p>

        <button
          onClick={() => signIn('github', { callbackUrl: '/' })}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-black px-4 py-2 font-medium text-white transition-colors hover:bg-gray-900/90"
        >
          <FontAwesomeIcon icon={faGithub} />
          Sign In with GitHub
        </button>
      </div>
    </div>
  )
}

export default LoginPageContent
