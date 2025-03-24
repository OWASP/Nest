'use client'
import { faMoon, faSun } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useTheme } from 'next-themes'
import { cn } from 'utils/utility'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from 'components/ui/tooltip'

export function ModeToggle({ className }: { className?: string }) {
  const { theme, setTheme } = useTheme()
  const isDark = theme === 'dark'

  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark')
  }

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <label className="relative inline-flex cursor-pointer items-center">
              <input
                type="checkbox"
                className="peer sr-only"
                checked={!isDark}
                onChange={toggleTheme}
                aria-label={isDark ? 'Enable light mode' : 'Enable dark mode'}
              />
              <button
                onClick={toggleTheme}
                className="relative h-10 w-10 transform rounded-full bg-[#87a1bc] transition-all duration-200 hover:ring-1 hover:ring-[#b0c7de] hover:ring-offset-0 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring active:scale-95 disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-[#46576b]"
                aria-label={isDark ? 'Enable light mode' : 'Enable dark mode'}
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <FontAwesomeIcon
                    icon={isDark ? faSun : faMoon}
                    className="h-5 w-5 transform text-gray-900 transition-all duration-300 hover:rotate-12 dark:text-gray-100"
                    fixedWidth
                  />
                </div>
              </button>
            </label>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            {isDark ? 'Enable light mode' : 'Enable dark mode'}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  )
}

export default ModeToggle
