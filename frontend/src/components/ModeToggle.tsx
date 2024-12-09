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
      <label className="relative inline-flex cursor-pointer items-center">
        <input type="checkbox" className="peer sr-only" checked={dark} onChange={darkModeHandler} />
        <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700"></div>
      </label>
      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
        <FontAwesomeIconWrapper icon="fa-solid fa-moon" />
      </span>
    </div>
  )
}

export default ModeToggle
