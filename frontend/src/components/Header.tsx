'use client'
import { Button } from '@heroui/button'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import {
  FaRegHeart,
  FaRegStar,
  FaHeart as FaSolidHeart,
  FaStar as FaSolidStar,
  FaBars,
  FaTimes,
} from 'react-icons/fa'
import { desktopViewMinWidth, headerLinks } from 'utils/constants'
import { cn } from 'utils/utility'
import ModeToggle from 'components/ModeToggle'
import NavButton from 'components/NavButton'
import NavDropdown from 'components/NavDropDown'
import UserMenu from 'components/UserMenu'

export default function Header({ isGitHubAuthEnabled }: { readonly isGitHubAuthEnabled: boolean }) {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)

  useEffect(() => {
    const handleResize = () => {
      if (globalThis.innerWidth >= desktopViewMinWidth) {
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

    globalThis.addEventListener('resize', handleResize)
    globalThis.addEventListener('click', handleOutsideClick)

    return () => {
      globalThis.removeEventListener('resize', handleResize)
      globalThis.removeEventListener('click', handleOutsideClick)
    }
  }, [mobileMenuOpen])

  return (
    <header className="bg-owasp-blue fixed inset-x-0 top-0 z-50 w-full shadow-md dark:bg-slate-800" role="banner">
      <div className="flex h-16 w-full items-center px-4 max-lg:justify-between" id="navbar-sticky">
        {/* Logo */}
        <Link 
          href="/" 
          onClick={() => setMobileMenuOpen(false)}
          aria-label="OWASP Nest Home"
          className="focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
        >
          <div className="flex h-full items-center">
            <div className="flex h-16 w-16 items-center justify-center py-2">
              <Image
                width={64}
                height={64}
                priority={true}
                src={'/img/logo_dark.png'}
                className="h-full w-auto object-contain"
                alt="OWASP Logo"
              />
            </div>
            <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
              Nest
            </div>
          </div>
        </Link>
        {/* Desktop Header Links */}
        <div className="hidden flex-1 justify-between rounded-lg pl-6 font-medium lg:block">
          <div className="flex justify-start pl-6">
            {headerLinks
              .filter((link) => {
                if (link.requiresGitHubAuth) {
                  return isGitHubAuthEnabled
                }
                return true
              })
              .map((link) => {
                return link.submenu ? (
                  <NavDropdown link={link} pathname={pathname} key={`${link.text}-${link.href}`} />
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
        <div className="flex items-center justify-normal gap-4">
          <div className="hidden md:flex">
            <NavButton
              href="https://github.com/OWASP/Nest"
              defaultIcon={FaRegStar}
              hoverIcon={FaSolidStar}
              defaultIconColor="#FDCE2D"
              hoverIconColor="#FDCE2D"
              text="Star"
            />
          </div>

          <div className="hidden md:flex">
            <NavButton
              href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
              defaultIcon={FaRegHeart}
              hoverIcon={FaSolidHeart}
              defaultIconColor="#b55f95"
              hoverIconColor="#d9156c"
              text="Sponsor"
            />
          </div>
          <div className="hidden md:flex">
            <UserMenu isGitHubAuthEnabled={isGitHubAuthEnabled} />
          </div>
          <ModeToggle />
          <div className="lg:hidden">
            <Button
              onPress={toggleMobileMenu}
              className="flex h-11 w-11 items-center justify-center bg-transparent text-slate-300 hover:bg-transparent hover:text-slate-100 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded"
              aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
              aria-expanded={mobileMenuOpen}
              aria-controls="mobile-menu"
            >
              <span className="sr-only">
                {mobileMenuOpen ? "Close main menu" : "Open main menu"}
              </span>
              {mobileMenuOpen ? <FaTimes className="h-6 w-6" /> : <FaBars className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>
      <div
        id="mobile-menu"
        className={cn(
          'bg-owasp-blue fixed inset-y-0 left-0 z-50 w-64 transform shadow-md transition-transform dark:bg-slate-800',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        role="navigation"
        aria-label="Mobile navigation menu"
      >
        <div className="flex h-full flex-col justify-between gap-1 px-2 pt-2 pb-3">
          {/* Logo */}
          <div className="flex flex-col justify-center gap-5">
            <Link href="/" onClick={() => setMobileMenuOpen(false)}>
              <div className="flex h-full items-center">
                <div className="flex h-16 w-16 items-center justify-center py-2">
                  <Image
                    width={64}
                    height={64}
                    priority={true}
                    src={'/img/logo_dark.png'}
                    className="h-full w-auto object-contain"
                    alt="OWASP Logo"
                  />
                </div>
                <div className="text-2xl text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
                  Nest
                </div>
              </div>
            </Link>
            {headerLinks
              .filter((link) => {
                if (link.requiresGitHubAuth) {
                  return isGitHubAuthEnabled
                }
                return true
              })
              .map((link) =>
                link.submenu ? (
                  <div key={link.text} className="flex flex-col gap-2">
                    <div className="block px-3 py-3 font-medium text-slate-700 dark:text-slate-300">
                      {link.text}
                    </div>
                    <div className="ml-4">
                      {link.submenu.map((sub) => (
                        <Link
                          key={`${sub.text}-${sub.href}`}
                          href={sub.href || '/'}
                          className={cn(
                            'block w-full px-4 py-3 text-left text-sm text-slate-700 transition duration-150 ease-in-out first:rounded-t-md last:rounded-b-md hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white',
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
                      'navlink block px-3 py-2 text-slate-700 transition duration-150 ease-in-out hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white',
                      pathname === link.href && 'font-bold text-blue-800 dark:text-white'
                    )}
                    onClick={toggleMobileMenu}
                  >
                    {link.text}
                  </Link>
                )
              )}
          </div>

          <div className="flex flex-col gap-y-2 md:hidden">
            <UserMenu isGitHubAuthEnabled={isGitHubAuthEnabled} />
            <NavButton
              href="https://github.com/OWASP/Nest"
              defaultIcon={FaRegStar}
              hoverIcon={FaSolidStar}
              defaultIconColor="#FDCE2D"
              hoverIconColor="#FDCE2D"
              text="Star On Github"
            />
            <NavButton
              href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
              defaultIcon={FaRegHeart}
              hoverIcon={FaSolidHeart}
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
