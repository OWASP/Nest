'use client'

import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useLogout } from 'hooks/useLogout'
import Image from 'next/image'
import { signIn, useSession } from 'next-auth/react'
import { useEffect, useId, useRef, useState } from 'react'
import { ExtendedSession } from 'types/auth'

export default function UserMenu({
  isGitHubAuthEnabled,
}: {
  readonly isGitHubAuthEnabled: boolean
}) {
  const { data: session, status } = useSession()
  const { logout, isLoggingOut } = useLogout()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const dropdownId = useId()
  const isProjectLeader = (session as ExtendedSession)?.user.isLeader

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (!isGitHubAuthEnabled) return null

  if (status === 'loading') {
    return (
      <div className="flex h-10 w-10 items-center justify-center">
        <div className="animate-pulse h-10 w-10 rounded-full bg-gray-300 dark:bg-slate-700" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return (
      <button
        onClick={() => signIn('github', { callbackUrl: '/', prompt: 'login' })}
        className="group relative flex h-10 items-center justify-center gap-2 rounded-md bg-[#87a1bc] p-4 text-sm font-medium text-black hover:ring-1 hover:ring-[#b0c7de] dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-[#46576b]"
      >
        <FontAwesomeIcon icon={faGithub} />
        Sign In
      </button>
    )
  }

  const handleLogout = () => {
    logout()
    setIsOpen(false)
  }

  return (
    <div ref={dropdownRef} className="relative flex items-center justify-center">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-controls={dropdownId}
        className="w-auto focus:outline-none"
        disabled={isLoggingOut}
      >
        <div className="h-10 w-10 overflow-hidden rounded-full">
          <Image
            src={session.user?.image ?? '/default-avatar.png'}
            alt="User avatar"
            width={40}
            height={40}
            className="h-full w-full object-cover"
          />
        </div>
      </button>

      {isOpen && (
        <div
          id={dropdownId}
          className="absolute right-0 top-full z-20 mt-2 w-48 overflow-hidden rounded-md bg-white shadow-lg dark:bg-slate-800"
        >
          {isProjectLeader && (
            <a
              href="/my/mentorship"
              className="block w-full px-4 py-2 text-left text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white"
            >
              My Mentorship
            </a>
          )}

          <button
            onClick={handleLogout}
            disabled={isLoggingOut}
            className="block w-full px-4 py-2 text-left text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white"
          >
            {isLoggingOut ? 'Signing out...' : 'Sign out'}
          </button>
        </div>
      )}
    </div>
  )
}
