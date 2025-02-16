import { faMoon, faSun } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { cn } from 'utils/utility'
import { Tooltip } from 'components/ui/tooltip'
import { useTheme } from './ThemeProvider'

function ModeToggle({ className }: { className?: string }) {
  const { dark, toggleTheme } = useTheme()

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
        <FontAwesomeIcon icon={dark ? faMoon : faSun} className="h-4 w-4" fixedWidth />
      </span>
      <Tooltip content={dark ? 'Enable light mode' : 'Enable dark mode'}>
        <label className="relative inline-flex cursor-pointer items-center">
          <input type="checkbox" className="peer sr-only" checked={!dark} onChange={toggleTheme} />
          <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-600 dark:bg-gray-700"></div>
        </label>
      </Tooltip>
    </div>
  )
}

export default ModeToggle
