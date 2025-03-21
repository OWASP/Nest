import { faMoon, faSun } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState, useEffect } from 'react'
import { cn } from 'utils/utility'
import { Tooltip } from 'components/ui/tooltip'

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
    <div className={cn('flex items-center', className)}>
      <Tooltip
        showArrow
        content={dark ? 'Enable light mode' : 'Enable dark mode'}
        positioning={{ placement: 'bottom-start' }}
        openDelay={100}
        closeDelay={100}
      >
        <button
          onClick={darkModeHandler}
          className="relative h-10 w-10 transform overflow-hidden rounded-full border border-gray-300 shadow-sm transition-all duration-200 hover:shadow-md focus:outline-none focus:ring-1 focus:ring-gray-600 active:scale-95 dark:border-gray-600"
          aria-label={dark ? 'Enable light mode' : 'Enable dark mode'}
        >
          <div className="absolute inset-0 bg-gray-100 transition-colors duration-300 dark:bg-gray-800"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <FontAwesomeIcon
              icon={!dark ? faMoon : faSun}
              className="h-5 w-5 transform text-gray-900 transition-all duration-300 hover:rotate-12 dark:text-gray-100"
              fixedWidth
            />
          </div>
          <div className="absolute inset-0 bg-gray-200 opacity-0 transition-opacity duration-200 hover:opacity-20 dark:bg-gray-700"></div>
        </button>
      </Tooltip>
    </div>
  )
}

export default ModeToggle
