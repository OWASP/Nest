import React from 'react'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'

const SecondaryCard = ({
  title = '',
  icon,
  children = null,
  className = '',
}: {
  title?: React.ReactNode
  icon?: IconType
  children?: React.ReactNode
  className?: string
}) => (
  <div className={`mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 ${className}`}>
    {title && (
      <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
        {icon && <IconWrapper icon={icon} className="h-5 w-5" />}
        {title}
      </h2>
    )}
    {children}
  </div>
)

export default SecondaryCard
