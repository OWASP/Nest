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
          className="relative h-10 w-10 transform rounded-full bg-[#87a1bc] transition-all duration-200 active:scale-95  hover:ring-1 hover:ring-[#b0c7de] hover:ring-offset-0 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-[#46576b]  "
          aria-label={dark ? 'Enable light mode' : 'Enable dark mode'}
        >
          <div className="absolute inset-0 flex items-center justify-center">
            <FontAwesomeIcon
              icon={dark ? faSun : faMoon}
              className="h-5 w-5 transform text-gray-900 transition-all duration-300 hover:rotate-12 dark:text-gray-100"
              fixedWidth
            />
          </div>
        </button>
      </Tooltip>
    </div>
  )
}

export default ModeToggle