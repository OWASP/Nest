import type React from 'react'
import { FaGraduationCap } from 'react-icons/fa6'

interface AccessDeniedDisplayProps {
  title?: string
  message?: string
}

const AccessDeniedDisplay: React.FC<AccessDeniedDisplayProps> = ({
  title = 'Access Denied',
  message = 'You do not have permission to access this page.',
}) => {
  return (
    <div className="flex flex-col items-center justify-center px-4 text-center">
      <FaGraduationCap className="mb-4 text-6xl text-red-400" />
      <h2 className="mb-2 text-2xl font-bold text-gray-600 dark:text-white">{title}</h2>
      <p className="text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  )
}

export default AccessDeniedDisplay
