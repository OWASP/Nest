import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import { useTheme } from 'next-themes'
import { useState, useEffect } from 'react'
import { MdLightMode, MdDarkMode } from 'react-icons/md'

export default function ModeToggle() {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()
  useEffect(() => {
    setMounted(true)
  }, [])

  const darkModeHandler = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  if (!mounted) return null

  return (
    <div className="flex items-center">
      <Tooltip
        showArrow
        placement="bottom-end"
        content={theme === 'dark' ? 'Enable light mode' : 'Enable dark mode'}
      >
        <Button
          onPress={darkModeHandler}
          className="focus-visible:ring-ring relative h-10 w-10 transform rounded-full bg-[#87a1bc] transition-all duration-200 hover:ring-1 hover:ring-[#b0c7de] hover:ring-offset-0 focus-visible:ring-1 focus-visible:outline-hidden active:scale-95 disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-[#46576b]"
          isIconOnly={true}
          aria-label={theme === 'dark' ? 'Enable light mode' : 'Enable dark mode'}
        >
          <div className="absolute inset-0 flex items-center justify-center">
            {theme === 'dark' ? (
              <MdLightMode className="h-5 w-5 text-white transition-all duration-300" />
            ) : (
              <MdDarkMode className="h-5 w-5 text-white transition-all duration-300" />
            )}
          </div>
        </Button>
      </Tooltip>
    </div>
  )
}
