'use client'

import { useDjangoSession } from 'hooks/useDjangoSession'
import { useLogout } from 'hooks/useLogout'
import Image from 'next/image'
import Link from 'next/link'
import { signIn } from 'next-auth/react'
import { useEffect, useId, useRef, useState } from 'react'
import { FaGithub } from 'react-icons/fa'

export default function UserMenu({
  isGitHubAuthEnabled,
}: {
  readonly isGitHubAuthEnabled: boolean
}) {
  const { isSyncing, session, status } = useDjangoSession()
  const { logout, isLoggingOut } = useLogout()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const dropdownId = useId()
  const isProjectLeader = session?.user?.isLeader
  const isOwaspStaff = session?.user?.isOwaspStaff

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

  if (isSyncing) {
    return (
      <div className="flex h-10 w-10 items-center justify-center">
        <div className="h-10 w-10 animate-pulse rounded-full bg-gray-300 dark:bg-slate-700" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return (
      <button
        type="button"
        onClick={() => signIn('github', { callbackUrl: '/', prompt: 'login' })}
        className="group relative flex h-10 cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-md border border-gray-300 bg-white px-4 text-sm font-medium text-gray-800 transition-all duration-200 hover:bg-gray-100 hover:border-gray-400 hover:shadow-sm focus-visible:ring-1 focus-visible:ring-blue-500 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-800 dark:hover:border-slate-500 dark:hover:shadow-md dark:hover:shadow-blue-500/20"
        >
        <FaGithub className="h-4 w-4" />
        <span className="relative inline-block after:absolute after:left-0 after:bottom-0 after:h-[1px] after:w-0 after:bg-gray-800 after:transition-all after:duration-300 group-hover:after:w-full dark:after:bg-white">
          Sign In
        </span>
      </button>
    )
  }

  const handleLogout = () => {
    logout()
    setIsOpen(false)
  }

  const userMenuItemClasses =
    'block w-full cursor-pointer px-4 py-2 text-left text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white'

  return (
    <div ref={dropdownRef} className="relative flex items-center justify-center">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-controls={dropdownId}
        className="w-auto cursor-pointer focus:outline-hidden"
        disabled={isLoggingOut}
      >
        <div className="h-10 w-10 overflow-hidden rounded-full">
          <Image
            src={session?.user?.image ?? '/default-avatar.png'}
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
          className="absolute top-full right-0 z-20 mt-2 w-48 overflow-hidden rounded-md bg-white shadow-lg dark:bg-slate-800"
        >
          {isProjectLeader && (
            <Link
              href="/my/mentorship"
              className={userMenuItemClasses}
              onClick={() => setIsOpen(false)}
            >
              My Mentorship
            </Link>
          )}

          {isOwaspStaff && (
            <Link
              href="/projects/dashboard"
              className={userMenuItemClasses}
              onClick={() => setIsOpen(false)}
            >
              Project Health Dashboard
            </Link>
          )}

          <button
            type="button"
            onClick={handleLogout}
            disabled={isLoggingOut}
            className={userMenuItemClasses}
          >
            {isLoggingOut ? 'Signing out...' : 'Sign out'}
          </button>
        </div>
      )}
    </div>
  )
}
