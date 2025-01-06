import { faBars, faTimes } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

import ModeToggle from './ModeToggle'
import { cn } from '../lib/utils'
import { headerLinks } from '../utils/constants'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)

  return (
    <header className="fixed inset-x-0 top-0 z-50 w-full max-w-[100vw] bg-owasp-blue shadow-md dark:bg-slate-800">
      <div className="flex h-16 w-full items-center px-4 max-md:justify-between" id="navbar-sticky">
        {/* Logo */}
        <NavLink to="/">
          <div className="flex h-full items-center">
            <img
              src={'/img/owasp_icon_white_sm.png'}
              className="hidden h-16 dark:block"
              alt="OWASP Logo"
            ></img>
            <img
              src={'/img/owasp_icon_black_sm.png'}
              className="block h-16 dark:hidden"
              alt="OWASP Logo"
            ></img>
            <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
              Nest
            </div>
          </div>
        </NavLink>
        {/* Desktop Header Links */}
        <div className="hidden flex-1 justify-between rounded-lg pl-6 font-medium md:block">
          <div className="flex justify-start pl-6">
            {headerLinks.map((link, i) => (
              <NavLink
                key={i}
                to={link.href}
                className={cn(
                  'navlink px-3 py-2 text-slate-700 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-200',
                  location.pathname === link.href && 'font-bold text-blue-800 dark:text-white'
                )}
                aria-current="page"
              >
                {link.text}
              </NavLink>
            ))}
          </div>
        </div>
        <div className="flex items-center justify-normal space-x-4">
          <ModeToggle />
          <div className="md:hidden">
            <button
              onClick={toggleMobileMenu}
              className="text-slate-300 hover:text-slate-100 focus:outline-none"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <FontAwesomeIcon icon={faTimes} className="h-6 w-6" />
              ) : (
                <FontAwesomeIcon icon={faBars} className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 transform bg-owasp-blue shadow-md transition-transform dark:bg-slate-800',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="space-y-1 px-2 pb-3 pt-2">
          {/* Logo */}
          <NavLink to="/">
            <div className="flex h-full items-center">
              <img
                src={'/img/owasp_icon_white_sm.png'}
                className="hidden h-16 dark:block"
                alt="OWASP Logo"
              ></img>
              <img
                src={'/img/owasp_icon_black_sm.png'}
                className="block h-16 dark:hidden"
                alt="OWASP Logo"
              ></img>
              <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
                Nest
              </div>
            </div>
          </NavLink>
          {headerLinks.map((link, i) => (
            <NavLink
              key={i}
              to={link.href}
              className={cn(
                'navlink block px-3 py-2 text-slate-700 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-200',
                location.pathname === link.href && 'font-bold text-blue-800 dark:text-white'
              )}
              onClick={toggleMobileMenu}
            >
              {link.text}
            </NavLink>
          ))}
        </div>
      </div>
    </header>
  )
}
