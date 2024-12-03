import { faMoon, faSun } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { headerLinks } from '../utils/constants'
import { NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'

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
      <div className="dark:bg-slate-800 bg-owasp-blue h-16">
        <div className="flex h-full items-center" id="navbar-sticky">
          <NavLink to="/">
            <div className="flex h-full items-center">
              <img
                src={
                  !dark
                    ? '../public/img/owasp_icon_black_sm.png'
                    : '../public/img/owasp_icon_white_sm.png'
                }
                className="h-16 px-2"
                alt="OWASP Logo"
              ></img>
              <div className="text-2xl dark:text-slate-300 text-slate-800 dark:hover:text-slate-200">
                Nest
              </div>
            </div>
          </NavLink>
          <div className="flex-1 pl-6 font-medium rounded-lg justify-between">
            <div className="flex pl-6 justify-start dark:text-slate-300 text-slate-700">
              {headerLinks.map((link, i) => (
                <NavLink
                  key={i}
                  to={link.href}
                  className="navlink py-2 px-3 dark:hover:text-slate-200 hover:text-slate-800"
                  aria-current="page"
                >
                  {link.text}
                </NavLink>
              ))}
            </div>
          </div>
          <div className="justify-end">
            <label className="inline-flex items-center content-center cursor-pointer">
              <span className="ms-3 pr-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                {icon}
              </span>
              <input
                onChange={toggleTheme}
                type="checkbox"
                value=""
                className="sr-only peer"
              ></input>
              <div className="relative w-9 h-5 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-500 peer-checked:bg-slate-500"></div>
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
