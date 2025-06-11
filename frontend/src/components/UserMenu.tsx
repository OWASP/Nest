'use client'

import { Dropdown, DropdownTrigger, DropdownMenu, DropdownItem, Skeleton } from '@heroui/react'
import Image from 'next/image'
import { useSession, signIn, signOut } from 'next-auth/react'
import { userAuthStatus } from 'utils/constants'

export default function UserMenu() {
  const { data: session, status } = useSession()

  if (status === userAuthStatus.LOADING) {
    return (
      <div className="flex h-10 w-10 items-center justify-center">
        <Skeleton className="h-10 w-10 rounded-full" />
      </div>
    )
  }

  if (!session) {
    return (
      <button
        onClick={() => signIn('github', { callbackUrl: '/', prompt: 'login' })}
        className="group relative flex h-10 w-full cursor-pointer items-center justify-center gap-2 overflow-hidden whitespace-pre rounded-md bg-[#87a1bc] px-4 py-2 text-sm font-medium text-black hover:ring-1 hover:ring-[#b0c7de] hover:ring-offset-0 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-[#46576b] md:flex"
      >
        Sign in
      </button>
    )
  }

  return (
    <Dropdown className="bg-owasp-blue dark:bg-slate-800">
      <DropdownTrigger>
        <Image
          src={session.user?.image || '/default-avatar.png'}
          height={40}
          width={40}
          alt="User avatar"
          className="h-10 w-10 cursor-pointer rounded-full object-cover"
        />
      </DropdownTrigger>

      <DropdownMenu className="w-48" variant="bordered">
        <DropdownItem
          key={'sign-out'}
          disableAnimation
          onClick={() => signOut({ callbackUrl: '/' })}
          className="relative flex h-10 w-full cursor-pointer items-center justify-center gap-2 whitespace-pre rounded-md bg-[#87a1bc] px-4 py-2 text-sm font-medium text-black focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white"
        >
          Sign out
        </DropdownItem>
      </DropdownMenu>
    </Dropdown>
  )
}
