import { faMoon, faSun, faBars, faTimes } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

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


export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)

  function toggleMenu() {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <div>
      <div className="fixed inset-x-0 top-0 z-50 bg-owasp-blue shadow-md dark:bg-slate-800">
        <div className="flex h-16 items-center justify-between" id="navbar-sticky">
          <div>
            <NavLink to="/">
              <div className="flex h-full items-center">
                <img
                  src={!dark ? '/img/owasp_icon_black_sm.png' : '/img/owasp_icon_white_sm.png'}
                  className="h-16 px-2"
                  alt="OWASP Logo"
                />
                <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
                  Nest
                </div>
              </div>
            </NavLink>
          </div>
          <div className="flex-1 justify-between rounded-lg pl-6 font-medium hidden md:flex">
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
          <div>
            <div className="flex justify-between items-center w-full p-4">
              <div className="flex items-center">
                <label className="inline-flex cursor-pointer content-center items-center">
                  <span className="ms-3 pr-2 text-sm font-medium text-gray-900 dark:text-gray-300">
                    {icon}
                  </span>
                  <input
                    onChange={toggleTheme}
                    type="checkbox"
                    className="peer sr-only"
                  />
                  <div className="peer relative h-5 w-9 rounded-full bg-gray-200 after:absolute after:start-[2px] after:top-[2px] after:h-4 after:w-4 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-slate-500 peer-checked:after:translate-x-full peer-checked:after:border-white rtl:peer-checked:after:-translate-x-full dark:border-gray-500 dark:bg-gray-700"></div>
                  <span className="ms-3 text-sm font-medium text-gray-900 dark:text-gray-300">
                    <i className="fa-regular fa-moon"></i>
                  </span>
                </label>
              </div>

              <button
                onClick={toggleMenu}
                className="ml-4 text-slate-700 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-200 md:hidden"
              >
                <FontAwesomeIcon icon={isMenuOpen ? faTimes : faBars} className="h-6 w-6" />
              </button>
            </div>
          </div>

        </div>
        <div
          className={`${isMenuOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'
            } overflow-hidden transition-all duration-300 ease-in-out md:hidden`}
        >
          <div className="space-y-1 px-4 pb-3 pt-2">
            {headerLinks.map((link, i) => (
              <NavLink
                key={i}
                to={link.href}
                className="block rounded-md px-3 py-2 text-base font-medium text-slate-700 hover:bg-slate-100 hover:text-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-slate-200"
                onClick={() => setIsMenuOpen(false)}
              >
                {link.text}
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </header>
  )
}
