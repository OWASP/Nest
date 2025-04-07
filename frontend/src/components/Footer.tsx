'use client'
import { faGithub, faSlack, faBluesky } from '@fortawesome/free-brands-svg-icons'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Image from 'next/image'
import Link from 'next/link'
import { useState, useCallback, useEffect } from 'react'
import type { Section } from 'types/section'
import { footerSections } from 'utils/constants'

export default function Footer() {
  // State to keep track of the open section in the footer
  const [openSection, setOpenSection] = useState<string | null>(null)
  // Track screen size to handle responsive behavior
  const [isMobile, setIsMobile] = useState<boolean>(false)

  // Function to toggle the section open/closed
  const toggleSection = useCallback((title: string) => {
    // If the section is already open, close it, otherwise open it
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024)
      if (window.innerWidth >= 1024) {
        setOpenSection(null)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)

    return () => window.removeEventListener('resize', handleResize)
  }, [])

  const socialLinks = [
    {
      icon: faBluesky,
      href: 'https://bsky.app/profile/nest.owasp.org',
      label: 'Bluesky',
    },
    {
      icon: faGithub,
      href: 'https://github.com/owasp/nest',
      label: 'GitHub',
    },
    {
      icon: faSlack,
      href: 'https://owasp.slack.com/archives/project-nest',
      label: 'Slack',
    },
  ]

  return (
    <footer className="mt-auto w-full border-t bg-slate-200 dark:bg-slate-800 xl:max-w-full">
      <div className="container mx-auto -mt-6 px-4 py-8 sm:py-12">
        <div className="grid gap-8 md:gap-12 lg:grid-cols-12">
          <div className="space-y-4 sm:space-y-6 lg:col-span-4">
            <div className="-mb-2 -ml-1.5 flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center sm:h-10 sm:w-10">
                <Image
                  src={'/img/owasp_icon_white_sm.png'}
                  alt="OWASP logo"
                  className="hidden dark:block"
                  width={48}
                  height={48}
                  priority
                />
                <Image
                  src={'/img/owasp_icon_black_sm.png'}
                  alt="OWASP logo"
                  className="block dark:hidden"
                  width={48}
                  height={48}
                  priority
                />
              </div>
              <h2 className="text-xl font-bold sm:text-2xl">OWASP Nest</h2>
            </div>
            <p className="max-w-md text-sm text-slate-600 dark:text-slate-400 sm:text-base">
              OWASP Nest promotes collaboration, making it easier for contributors to engage
              meaningfully with OWASP's mission to improve software security.
            </p>
            <div className="flex items-center gap-2 sm:gap-3">
              {socialLinks.map((social) => (
                <Link
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`OWASP Nest ${social.label}`}
                  className="group"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-300 transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg dark:bg-slate-700 sm:h-10 sm:w-10">
                    <FontAwesomeIcon
                      icon={social.icon}
                      className="h-4 w-4 text-slate-700 transition-colors duration-300 group-hover:text-blue-600 dark:text-slate-300 dark:group-hover:text-blue-400 sm:h-5 sm:w-5"
                      aria-hidden="true"
                    />
                  </div>
                </Link>
              ))}
            </div>
          </div>

          <nav className="lg:col-span-8" aria-label="Footer navigation">
            <div className="grid grid-cols-2 gap-4 sm:gap-6 md:grid-cols-4 md:gap-4 lg:gap-8">
              {footerSections.map((section: Section) => (
                <div key={section.title} className="space-y-3 sm:space-y-4">
                  <button
                    onClick={() => toggleSection(section.title)}
                    className="group flex w-full items-center justify-between bg-transparent text-left text-base font-semibold sm:text-lg lg:cursor-default"
                    aria-expanded={isMobile ? openSection === section.title : true}
                    aria-controls={`footer-section-${section.title.toLowerCase().replace(/\s+/g, '-')}`}
                    tabIndex={isMobile ? 0 : -1}
                    disabled={!isMobile}
                  >
                    <h3 className="relative pb-1 text-left transition-colors duration-200 group-hover:text-slate-600 dark:group-hover:text-blue-400 sm:pb-2">
                      {section.title}
                      <div className="absolute bottom-0 left-0 h-0.5 w-6 origin-left transform bg-slate-500 transition-all duration-300 group-hover:w-full group-hover:bg-slate-600 dark:bg-blue-500 dark:group-hover:bg-blue-400 sm:w-8" />
                    </h3>

                    {isMobile && (
                      <span className="transition-transform duration-200">
                        <FontAwesomeIcon
                          icon={openSection === section.title ? faChevronUp : faChevronDown}
                          className="h-3 w-3 sm:h-4 sm:w-4"
                          aria-hidden="true"
                        />
                      </span>
                    )}
                  </button>
                  <ul
                    id={`footer-section-${section.title.toLowerCase().replace(/\s+/g, '-')}`}
                    className={`space-y-2 overflow-hidden text-xs transition-all duration-300 ease-in-out sm:space-y-3 sm:text-sm lg:max-h-full ${
                      isMobile
                        ? openSection === section.title
                          ? 'max-h-96'
                          : 'max-h-0'
                        : 'max-h-full'
                    }`}
                    aria-hidden={isMobile && openSection !== section.title}
                  >
                    {section.links.map((link, index) => (
                      <li
                        key={index}
                        className="transform py-0.5 transition-transform duration-200 hover:translate-x-1 sm:py-1"
                      >
                        {link.isSpan ? (
                          <span className="text-slate-600 dark:text-slate-400">{link.text}</span>
                        ) : (
                          <Link
                            target={link.href.startsWith('http') ? '_blank' : undefined}
                            rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                            className="group relative text-slate-600 transition-colors duration-200 hover:text-slate-800 dark:text-slate-400 dark:hover:text-blue-400"
                            href={link.href}
                          >
                            {link.text}
                            <div className="absolute bottom-0 left-0 h-0.5 w-0 origin-left transform bg-slate-400 opacity-0 transition-all duration-300 group-hover:w-full group-hover:opacity-100 dark:bg-blue-400" />
                          </Link>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </nav>
        </div>

        <div className="my-6 h-px w-full bg-gradient-to-r from-transparent via-slate-300 to-transparent dark:via-slate-600 sm:my-8" />

        <div className="-mb-5 grid w-full place-content-center sm:mt-8">
          <div className="flex w-full flex-col items-center gap-3 text-center sm:flex-row sm:justify-between sm:gap-4 sm:text-left">
            <p className="text-xs text-slate-600 dark:text-slate-400 sm:text-sm">
              © <span>{new Date().getFullYear()}</span> OWASP Nest. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
