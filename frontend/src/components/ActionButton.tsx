import React, { ReactNode } from 'react'

interface ActionButtonProps {
  link?: string
  onClick?: () => void
  children: ReactNode
}

const ActionButton: React.FC<ActionButtonProps> = ({ link, onClick, children }) => {
  const baseStyles =
    'flex justify-center items-center gap-2 p-1 px-2 rounded-md bg-transparent hover:bg-[#0D6EFD] text-[#0D6EFD] hover:text-white dark:text-white border border-[#0D6EFD] dark:border-0 '

  return link ? (
    <a href={link} target="_blank" rel="noopener noreferrer" className={baseStyles}>
      {children}
    </a>
  ) : (
    <button onClick={onClick} className={baseStyles}>
      {children}
    </button>
  )
}

export default ActionButton
