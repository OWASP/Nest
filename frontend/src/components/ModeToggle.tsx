import { useState, useEffect } from 'react'
import { cn } from '../lib/utils'
import FontAwesomeIconWrapper from '../lib/FontAwesomeIconWrapper'

function ModeToggle({ className }: { className?: string }) {
  const [dark, setDark] = useState(() => {
    return localStorage.getItem('theme') === 'dark'
  })

  useEffect(() => {
    if (dark) {
      document.body.classList.add('dark')
    } else {
      document.body.classList.remove('dark')
    }
  }, [dark])

  const darkModeHandler = () => {
    setDark(!dark)
    const newTheme = !dark ? 'dark' : 'light'
    document.body.classList.toggle('dark', !dark)
    localStorage.setItem('theme', newTheme)
  }

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
        <FontAwesomeIconWrapper icon="fa-regular fa-lightbulb" />
      </span>
      <label className="relative inline-flex items-center cursor-pointer">
        <input type="checkbox" className="sr-only peer" checked={dark} onChange={darkModeHandler} />
        <div className="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
      </label>
      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
        <FontAwesomeIconWrapper icon="fa-solid fa-moon" />
      </span>
    </div>
  )
}

export default ModeToggle
