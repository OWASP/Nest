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
import GlobalSearch from 'components/GlobalSearch'
import ModeToggle from 'components/ModeToggle'
import NavButton from 'components/NavButton'
import NavDropdown from 'components/NavDropDown'
import UserMenu from 'components/UserMenu'

/**
 * Site header with the logo, desktop navigation links, and action buttons.
 * On mobile it shows the theme toggle, search, and menu buttons, and a slide-out sidebar.
 */
export default function Header({ isGitHubAuthEnabled }: { readonly isGitHubAuthEnabled: boolean }) {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  const logoSrc = '/img/logo_dark.png'

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
    <header className="bg-owasp-blue fixed inset-x-0 top-0 z-50 w-full shadow-md dark:bg-slate-800">
      <div
        className="flex h-16 w-full items-center max-lg:justify-between max-lg:pr-2 lg:px-4"
        id="navbar-sticky"
      >
        {/* Logo */}
        <Link
          href="/"
          onClick={() => setMobileMenuOpen(false)}
          className="rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
        >
          <div className="flex h-full items-center">
            <div className="flex h-16 w-16 items-center justify-center py-2">
              <Image
                width={64}
                height={64}
                priority={true}
                src={logoSrc}
                className="h-full w-auto object-contain"
                alt="OWASP Logo"
              />
            </div>
            <div className="text-2xl font-semibold text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
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
                      'navlink px-3 py-2 text-slate-700 transition-colors duration-200 hover:text-white dark:text-slate-300 dark:hover:text-blue-400',
                      pathname === link.href && 'font-bold text-blue-800 dark:text-white'
                    )}
                    aria-current={pathname === link.href ? 'page' : undefined}
                  >
                    {link.text}
                  </Link>
                )
              })}
          </div>
        </div>
        <div className="ml-auto flex items-center justify-normal gap-1 pl-2 md:gap-4 md:pl-4">
          <div className="max-md:order-2 max-md:flex max-md:h-11 max-md:w-11 max-md:items-center max-md:justify-center md:contents">
            <GlobalSearch />
          </div>
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

          <div className="max-md:order-1 max-md:flex max-md:h-11 max-md:w-11 max-md:items-center max-md:justify-center md:contents">
            <ModeToggle />
          </div>

          <div className="max-md:order-3 lg:hidden">
            <Button
              onPress={toggleMobileMenu}
              className="-ml-1 flex h-11 w-11 min-w-0 items-center justify-center rounded-lg bg-transparent p-0 text-slate-300 hover:bg-transparent hover:text-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <FaTimes className="h-6.5 w-6.5" />
              ) : (
                <FaBars className="h-7 w-7" />
              )}
            </Button>
          </div>
        </div>
      </div>
      <div
        className={cn(
          'bg-owasp-blue fixed inset-y-0 left-0 z-50 w-64 transform shadow-md transition-transform dark:bg-slate-800',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col justify-between gap-1 px-2 pt-2 pb-3">
          {/* Logo */}
          <div className="flex flex-col justify-center gap-5">
            <Link
              href="/"
              onClick={() => setMobileMenuOpen(false)}
              className="rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              <div className="flex h-full items-center">
                <div className="flex h-16 w-16 items-center justify-center py-2">
                  <Image
                    width={64}
                    height={64}
                    priority={true}
                    src={logoSrc}
                    className="h-full w-auto object-contain"
                    alt="OWASP Logo"
                  />
                </div>
                <div className="text-2xl font-semibold text-slate-800 dark:text-slate-300 dark:hover:text-slate-200">
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
