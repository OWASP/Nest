import { faMoon, faSun } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState, useEffect } from 'react'

import { cn } from 'utils/utility'

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
      <FontAwesomeIcon
        icon={dark ? faMoon : faSun}
        className="h-4 w-4 text-gray-900 dark:text-gray-100"
        fixedWidth
        aria-hidden="true"
      />
      <label
        htmlFor="theme-toggle"
        className="relative inline-flex cursor-pointer items-center"
      >
        <input
          id="theme-toggle"
          type="checkbox"
          className="peer sr-only"
          checked={!dark}
          onChange={darkModeHandler}
          aria-label="Toggle dark mode"
        />
        <div
          className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700"
          aria-hidden="true"
        />
        <span className="sr-only">Toggle dark mode</span>
      </label>
    </div>
  )
}

export default ModeToggle
