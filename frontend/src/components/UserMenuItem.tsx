import { FC, ReactNode } from 'react'

const UserMenuItem: FC<{
  onClick: () => void
  disabled?: boolean
  children: ReactNode
}> = ({ onClick, disabled, children }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="block w-full px-4 py-2 text-left text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white"
    >
      {children}
    </button>
  )
}

export default UserMenuItem
