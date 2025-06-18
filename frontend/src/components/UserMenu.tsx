'use client'

import Image from 'next/image'
import { useSession, signIn, signOut } from 'next-auth/react'
import { useEffect, useId, useRef, useState } from 'react'
import { userAuthStatus } from 'utils/constants'

type UserMenuProps = {
  isAuthEnabled: boolean
}

export default function UserMenu({ isAuthEnabled }: UserMenuProps) {
  const { data: session, status } = useSession()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const dropdownId = useId()

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (!isAuthEnabled) {
    return null
  }

  if (status === userAuthStatus.LOADING) {
    return (
      <div className="flex h-10 w-10 items-center justify-center">
        <div className="animate-pulse h-10 w-10 rounded-full bg-gray-300 dark:bg-slate-700" />
      </div>
    )
  }

  if (!session) {
    return (
      <button
        onClick={() => signIn('github', { callbackUrl: '/', prompt: 'login' })}
        className="group relative flex h-10 w-full cursor-pointer items-center justify-center gap-2 overflow-hidden whitespace-pre rounded-md bg-[#87a1bc] px-4 py-2 text-sm font-medium text-black hover:ring-1 hover:ring-[#b0c7de] hover:ring-offset-0 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-[#46576b]"
      >
        Sign in
      </button>
    )
  }

  return (
    <div ref={dropdownRef} className="relative flex items-center justify-center">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-controls={dropdownId}
        className="w-auto focus:outline-none"
      >
        <div className="h-10 w-10 overflow-hidden rounded-full">
          <Image
            src={session.user?.image || '/default-avatar.png'}
            height={40}
            width={40}
            alt="User avatar"
            className="h-full w-full object-cover"
          />
        </div>
      </button>

      {isOpen && (
        <div
          id={dropdownId}
          className="absolute right-0 top-full z-20 mt-2 w-48 overflow-hidden rounded-md bg-white shadow-lg dark:bg-slate-800"
        >
          <button
            onClick={() => {
              signOut({ callbackUrl: '/' })
              setIsOpen(false)
            }}
            className="block w-full px-4 py-2 text-left text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white"
          >
            Sign out
          </button>
        </div>
      )}
    </div>
  )
}
