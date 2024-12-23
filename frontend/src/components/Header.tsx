import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMoon, faSun, faBars, faTimes } from '@fortawesome/free-solid-svg-icons'

import { headerLinks } from '../utils/constants'

export default function Header() {
  const [dark, setDark] = useState(() => {
    return localStorage.getItem('theme') === 'dark'
  })
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const icon = !dark ? <FontAwesomeIcon icon={faSun} /> : <FontAwesomeIcon icon={faMoon} />

  useEffect(() => {
    if (dark) {
      document.body.classList.add('dark')
    } else {
      document.body.classList.remove('dark')
    }
  }, [dark])

  function toggleTheme() {
    setDark(!dark)
    const newTheme = !dark ? 'dark' : 'light'
    document.body.classList.toggle('dark', !dark)
    localStorage.setItem('theme', newTheme)
  }

  function toggleMenu() {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <header className="sticky top-0 z-50 bg-owasp-blue dark:bg-slate-800">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <NavLink to="/" className="flex items-center">
            <img
              src={
                !dark
                  ? '../public/img/owasp_icon_black_sm.png'
                  : '../public/img/owasp_icon_white_sm.png'
              }
              className="h-12 w-auto"
              alt="OWASP Logo"
            />
            <span className="ml-2 text-2xl font-bold text-slate-800 dark:text-slate-300">Nest</span>
          </NavLink>
          <div className="hidden items-center space-x-4 md:flex">
            {headerLinks.map((link, i) => (
              <NavLink
                key={i}
                to={link.href}
                className="navlink px-3 py-2 text-slate-700 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-200"
                aria-current="page"
              >
                {link.text}
              </NavLink>
            ))}
          </div>
          <div className="flex items-center">
            <label className="mr-4 inline-flex cursor-pointer items-center">
              <span className="mr-2 text-slate-700 dark:text-slate-300">{icon}</span>
              <input
                onChange={toggleTheme}
                type="checkbox"
                checked={dark}
                className="peer sr-only"
              />
              <div className="peer relative h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-slate-500 peer-checked:after:translate-x-full peer-checked:after:border-white dark:border-gray-500 dark:bg-gray-700"></div>
            </label>
            <button
              onClick={toggleMenu}
              className="text-slate-700 hover:text-slate-800 md:hidden dark:text-slate-300 dark:hover:text-slate-200"
            >
              <FontAwesomeIcon icon={isMenuOpen ? faTimes : faBars} size="lg" />
            </button>
          </div>
        </div>
      </div>
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out md:hidden ${
          isMenuOpen ? 'max-h-64' : 'max-h-0'
        }`}
      >
        <div className="space-y-1 px-2 pb-3 pt-2 sm:px-3">
          {headerLinks.map((link, i) => (
            <NavLink
              key={i}
              to={link.href}
              className="block rounded-md px-3 py-2 text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-slate-200"
              aria-current="page"
              onClick={() => setIsMenuOpen(false)}
            >
              {link.text}
            </NavLink>
          ))}
        </div>
      </div>
    </header>
  )
}
