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
import { headerLinks } from 'utils/constants'
import { cn } from 'utils/utility'
import GlobalSearch from 'components/GlobalSearch'
import ModeToggle from 'components/ModeToggle'
import NavButton from 'components/NavButton'
import NavDropdown from 'components/NavDropDown'
import UserMenu from 'components/UserMenu'

const DESKTOP_NAV_MIN_WIDTH = 1024 // Tailwind lg

export default function Header({ isGitHubAuthEnabled }: { readonly isGitHubAuthEnabled: boolean }) {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)
  const closeMobileMenu = () => setMobileMenuOpen(false)
  const logoSrc = '/img/logo_dark.png'
  const visibleLinks = headerLinks.filter(
    (link) => !link.requiresGitHubAuth || isGitHubAuthEnabled
  )

  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [mobileMenuOpen])

  useEffect(() => {
    const handleResize = () => {
      if (globalThis.innerWidth >= DESKTOP_NAV_MIN_WIDTH) {
        setMobileMenuOpen(false)
      }
    }

    const handleOutsideClick = (event: Event) => {
      const navbar = document.getElementById('navbar-sticky')
      const drawer = document.getElementById('mobile-drawer')
      if (
        mobileMenuOpen &&
        navbar &&
        !navbar.contains(event.target as Node) &&
        drawer &&
        !drawer.contains(event.target as Node)
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
        className="flex h-16 w-full min-w-0 items-center gap-2 px-3 sm:gap-3 sm:px-4 max-lg:justify-between"
        id="navbar-sticky"
      >
        {/* Logo */}
        <Link
          href="/"
          onClick={closeMobileMenu}
          className="shrink-0 rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
        >
          <div className="flex h-full items-center">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center py-1 xl:h-16 xl:w-16 xl:py-2">
              <Image
                width={64}
                height={64}
                priority={true}
                src={logoSrc}
                className="h-full w-auto object-contain"
                alt="OWASP Logo"
              />
            </div>
            <div className="hidden text-xl font-semibold text-slate-800 sm:block xl:text-2xl dark:text-slate-300 dark:hover:text-slate-200">
              Nest
            </div>
          </div>
        </Link>
        <nav
          aria-label="Main"
          className="hidden flex-1 items-center pl-2 font-medium lg:flex"
        >
          <div className="flex items-center gap-1">
            {visibleLinks.map((link) => {
              return link.submenu ? (
                <NavDropdown link={link} pathname={pathname} key={`${link.text}-${link.href}`} />
              ) : (
                <Link
                  key={link.text}
                  href={link.href || '/'}
                  className={cn(
                    'navlink shrink-0 whitespace-nowrap px-2 py-2 text-sm text-slate-700 transition-colors duration-200 hover:text-white xl:px-3 xl:text-base dark:text-slate-300 dark:hover:text-blue-400',
                    pathname === link.href && 'font-bold text-blue-800 dark:text-white'
                  )}
                  aria-current={pathname === link.href ? 'page' : undefined}
                >
                  {link.text}
                </Link>
              )
            })}
          </div>
        </nav>
        <div className="flex min-w-0 shrink items-center gap-2 sm:gap-3 lg:gap-2 xl:gap-3">
          <GlobalSearch />
          <div id="header-bar-actions" className="hidden shrink-0 items-center gap-2 lg:flex">
            <NavButton
              href="https://github.com/OWASP/Nest"
              defaultIcon={FaRegStar}
              hoverIcon={FaSolidStar}
              defaultIconColor="#FDCE2D"
              hoverIconColor="#FDCE2D"
              text="Star"
            />
            <NavButton
              href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
              defaultIcon={FaRegHeart}
              hoverIcon={FaSolidHeart}
              defaultIconColor="#b55f95"
              hoverIconColor="#d9156c"
              text="Sponsor"
            />
            <UserMenu isGitHubAuthEnabled={isGitHubAuthEnabled} />
          </div>
          <ModeToggle />
          <div className="shrink-0 lg:hidden">
            <Button
              onPress={toggleMobileMenu}
              className="flex h-11 w-11 items-center justify-center rounded-lg bg-transparent text-slate-300 hover:bg-transparent hover:text-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? <FaTimes className="h-6 w-6" /> : <FaBars className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-xs transition-opacity lg:hidden"
          onClick={closeMobileMenu}
          aria-hidden="true"
        />
      )}

      <div
        id="mobile-drawer"
        className={cn(
          'bg-owasp-blue fixed inset-y-0 left-0 z-50 w-64 transform shadow-md transition-transform lg:hidden dark:bg-slate-800',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col justify-between gap-1 px-2 pt-2 pb-3">
          <div className="flex flex-col justify-center gap-5">
            <Link
              href="/"
              onClick={closeMobileMenu}
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
            {visibleLinks.map((link) =>
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
                        onClick={closeMobileMenu}
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
                  onClick={closeMobileMenu}
                >
                  {link.text}
                </Link>
              )
            )}
          </div>

          <div id="mobile-drawer-actions" className="flex flex-col gap-y-2 lg:hidden">
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
