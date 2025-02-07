import { Button } from '@chakra-ui/react'
import { faHeart as faRegularHeart } from '@fortawesome/free-regular-svg-icons' // Outline Heart
import { faStar as faRegularStar } from '@fortawesome/free-regular-svg-icons'
import { faBars, faTimes } from '@fortawesome/free-solid-svg-icons'
import { faHeart as faSolidHeart } from '@fortawesome/free-solid-svg-icons'
import { faStar as faSolidStar } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { desktopViewMinWidth, headerLinks } from 'utils/constants'

import { cn } from 'utils/utility'
import ModeToggle from './ModeToggle'
import NavButton from './NavButton'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= desktopViewMinWidth) {
        setMobileMenuOpen(false)
      }
    }

    const handleOutsideClick = (event) => {
      const navbar = document.getElementById('navbar-sticky')
      const sidebar = document.querySelector('.fixed.inset-y-0')
      if (
        mobileMenuOpen &&
        navbar &&
        !navbar.contains(event.target) &&
        sidebar &&
        !sidebar.contains(event.target)
      ) {
        setMobileMenuOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    window.addEventListener('click', handleOutsideClick)

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('click', handleOutsideClick)
    }
  }, [mobileMenuOpen])

  return (
    <header className="fixed inset-x-0 top-0 z-50 w-full max-w-[100vw] bg-owasp-blue shadow-md dark:bg-slate-800">
      <div className="flex h-16 w-full items-center px-4 max-md:justify-between" id="navbar-sticky">
        {/* Logo */}
        <NavLink to="/" onClick={() => setMobileMenuOpen(false)}>
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
          <NavButton
            href="https://github.com/OWASP/Nest"
            defaultIcon={faRegularStar}
            hoverIcon={faSolidStar}
            defaultIconColor="text-white"
            hoverIconColor="text-yellow-400"
            text="Star"
            className="hidden"
          />

          <NavButton
            href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
            defaultIcon={faRegularHeart}
            hoverIcon={faSolidHeart}
            defaultIconColor="#b55f95"
            hoverIconColor="#d9156c"
            text="Sponsor"
          />
          <ModeToggle />
          <div className="md:hidden">
            <Button
              onClick={toggleMobileMenu}
              className="text-slate-300 hover:text-slate-100 focus:outline-none"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <FontAwesomeIcon icon={faTimes} className="h-6 w-6" />
              ) : (
                <FontAwesomeIcon icon={faBars} className="h-6 w-6" />
              )}
            </Button>
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
          <NavLink to="/" onClick={() => setMobileMenuOpen(false)}>
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
