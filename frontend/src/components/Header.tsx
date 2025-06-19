'use client'
import { faHeart as faRegularHeart } from '@fortawesome/free-regular-svg-icons'
import { faStar as faRegularStar } from '@fortawesome/free-regular-svg-icons'
import { faBars, faTimes } from '@fortawesome/free-solid-svg-icons'
import { faHeart as faSolidHeart } from '@fortawesome/free-solid-svg-icons'
import { faStar as faSolidStar } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import { desktopViewMinWidth, headerLinks } from 'utils/constants'
import { cn } from 'utils/utility'
import ModeToggle from 'components/ModeToggle'
import NavButton from 'components/NavButton'
import NavDropdown from 'components/NavDropDown'

export default function Header() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= desktopViewMinWidth) {
        setMobileMenuOpen(false)
      }
    }

    const handleOutsideClick = (event: Event) => {
      const navbar = document.getElementById('navbar-sticky')
      const sidebar = document.querySelector('.fixed.inset-y-0')
      if (
        mobileMenuOpen &&
        navbar &&
        !navbar.contains(event.target as Node) &&
        sidebar &&
        !sidebar.contains(event.target as Node)
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
        <Link href="/" onClick={() => setMobileMenuOpen(false)}>
          <div className="flex h-full items-center">
            <Image
              width={64}
              height={64}
              priority={true}
              src={'/img/owasp_icon_white_sm.png'}
              className="hidden dark:block"
              alt="OWASP Logo"
            />
            <Image
              width={64}
              height={64}
              priority={true}
              src={'/img/owasp_icon_black_sm.png'}
              className="block dark:hidden"
              alt="OWASP Logo"
            />
            <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
              Nest
            </div>
          </div>
        </Link>
        {/* Desktop Header Links */}
        <div className="hidden flex-1 justify-between rounded-lg pl-6 font-medium md:block">
          <div className="flex justify-start pl-6">
            {headerLinks.map((link, i) => {
              return link.submenu ? (
                <NavDropdown link={link} pathname={pathname} key={i} />
              ) : (
                <Link
                  key={link.text}
                  href={link.href || '/'}
                  className={cn(
                    'navlink px-3 py-2 text-slate-700 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-200',
                    pathname === link.href && 'font-bold text-blue-800 dark:text-white'
                  )}
                  aria-current="page"
                >
                  {link.text}
                </Link>
              )
            })}
          </div>
        </div>
        <div className="flex items-center justify-normal space-x-4">
          <NavButton
            href="https://github.com/OWASP/Nest"
            defaultIcon={faRegularStar}
            hoverIcon={faSolidStar}
            defaultIconColor="#FDCE2D"
            hoverIconColor="#FDCE2D"
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
            className="hidden"
          />
          <ModeToggle />
          <div className="md:hidden">
            <Button
              onPress={toggleMobileMenu}
              className="bg-transparent text-slate-300 hover:bg-transparent hover:text-slate-100 focus:outline-none"
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
        <div className="flex h-full flex-col justify-between space-y-1 px-2 pb-3 pt-2">
          {/* Logo */}
          <div className="flex flex-col justify-center gap-1">
            <Link href="/" onClick={() => setMobileMenuOpen(false)}>
              <div className="flex h-full items-center">
                <Image
                  width={64}
                  height={64}
                  priority={true}
                  src={'/img/owasp_icon_white_sm.png'}
                  className="hidden h-16 dark:block"
                  alt="OWASP Logo"
                />
                <Image
                  width={64}
                  height={64}
                  priority={true}
                  src={'/img/owasp_icon_black_sm.png'}
                  className="block h-16 dark:hidden"
                  alt="OWASP Logo"
                />
                <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
                  Nest
                </div>
              </div>
            </Link>
            {headerLinks.map((link) =>
              link.submenu ? (
                <div key={link.text} className="flex flex-col">
                  <div className="block px-3 py-2 font-medium text-slate-700 dark:text-slate-300">
                    {link.text}
                  </div>
                  <div className="ml-4">
                    {link.submenu.map((sub, i) => (
                      <Link
                        key={i}
                        href={sub.href || '/'}
                        className={cn(
                          'block w-full px-4 py-2 text-left text-sm text-slate-700 transition duration-150 ease-in-out first:rounded-t-md last:rounded-b-md hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white',
                          pathname === sub.href &&
                            'bg-blue-50 font-medium text-blue-600 dark:bg-blue-900/20 dark:text-blue-200'
                        )}
                        onClick={toggleMobileMenu}
                      >
                        {sub.text}
                      </Link>
                    ))}
                  </div>
                </div>
              ) : (
                <Link
                  key={link.text}
                  href={link.href || '/'}
                  className={cn(
                    'navlink block px-3 py-2 text-slate-700 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-200',
                    pathname === link.href && 'font-bold text-blue-800 dark:text-white'
                  )}
                  onClick={toggleMobileMenu}
                >
                  {link.text}
                </Link>
              )
            )}
          </div>

          <div className="flex flex-col gap-y-2">
            <NavButton
              href="https://github.com/OWASP/Nest"
              defaultIcon={faRegularStar}
              hoverIcon={faSolidStar}
              defaultIconColor="#FDCE2D"
              hoverIconColor="#FDCE2D"
              text="Star On Github"
            />
            <NavButton
              href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
              defaultIcon={faRegularHeart}
              hoverIcon={faSolidHeart}
              defaultIconColor="#b55f95"
              hoverIconColor="#d9156c"
              text="Sponsor Us"
            />
          </div>
        </div>
      </div>
    </header>
  )
}
