import { faChevronDown } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import { useState, useRef, useEffect, useId } from 'react'
import type { Link as LinkType } from 'types/link'
import { cn } from 'utils/utility'

interface NavDropDownProps {
  pathname: string
  link: LinkType
}

export default function NavDropdown({ link, pathname }: NavDropDownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)
  const dropdownId = useId()

  // For closing dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div
      ref={dropdownRef}
      className={cn(
        'dropdown navlink relative px-3 py-2 text-slate-700 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-200',
        link.submenu.map((sub) => sub.href).includes(pathname) &&
          'font-bold text-blue-800 dark:text-white'
      )}
    >
      <button
        className="flex items-center gap-2 whitespace-nowrap"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-controls={dropdownId}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            setIsOpen((prev) => !prev)
          } else if (e.key === 'Escape' && isOpen) {
            setIsOpen(false)
          }
        }}
      >
        <span className="inline-block">{link.text}</span>
        <span
          className="transition-transform duration-200"
          aria-hidden="true"
          style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}
        >
          <FontAwesomeIcon icon={faChevronDown} className="h-3 w-3" />
        </span>
      </button>
      {isOpen && (
        <div
          id={dropdownId}
          className="absolute left-0 top-full z-10 mt-1 w-48 overflow-hidden rounded-md bg-white shadow-lg dark:bg-slate-800"
        >
          {link.submenu.map((submenu, idx) => (
            <Link
              key={idx}
              href={submenu.href || '/'}
              className={cn(
                'block w-full px-4 py-2 text-left text-sm transition-colors',
                pathname === submenu.href
                  ? 'dark:bg-slate-650 bg-slate-500 font-bold text-white dark:text-white'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white'
              )}
              onClick={() => setIsOpen(false)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  setIsOpen(false)
                } else if (e.key === 'Escape') {
                  setIsOpen(false)
                }
              }}
            >
              {submenu.text}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
