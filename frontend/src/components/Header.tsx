import { faMoon, faSun } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { headerLinks } from 'utils/constants'

export default function Header() {
  const [dark, setDark] = useState(() => {
    return localStorage.getItem('theme') === 'dark'
  })
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

  return (
    <div>
      <div className="fixed inset-x-0 top-0 z-50 bg-owasp-blue shadow-md dark:bg-slate-800">
        <div className="flex h-16 items-center" id="navbar-sticky">
          <NavLink to="/">
            <div className="flex h-full items-center">
              <img
                src={!dark ? '/img/owasp_icon_black_sm.png' : '/img/owasp_icon_white_sm.png'}
                className="h-16 px-2"
                alt="OWASP Logo"
              ></img>
              <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
                Nest
              </div>
            </div>
          </NavLink>
          <div className="flex-1 justify-between rounded-lg pl-6 font-medium">
            <div className="flex justify-start pl-6 text-slate-700 dark:text-slate-300">
              {headerLinks.map((link, i) => (
                <NavLink
                  key={i}
                  to={link.href}
                  className="navlink px-3 py-2 hover:text-slate-800 dark:hover:text-slate-200"
                  aria-current="page"
                >
                  {link.text}
                </NavLink>
              ))}
            </div>
          </div>
          <div className="justify-end">
            <label className="inline-flex cursor-pointer content-center items-center">
              <span className="ms-3 pr-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                {icon}
              </span>
              <input
                onChange={toggleTheme}
                type="checkbox"
                value=""
                className="peer sr-only"
              ></input>
              <div className="peer relative h-5 w-9 rounded-full bg-gray-200 after:absolute after:start-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-slate-500 peer-checked:after:translate-x-full peer-checked:after:border-white rtl:peer-checked:after:-translate-x-full dark:border-gray-500 dark:bg-gray-700"></div>
              <span className="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">
                <i className="fa-regular fa-moon"></i>
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}
