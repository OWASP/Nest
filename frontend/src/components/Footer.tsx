'use client'
import { Button } from '@heroui/button'
import Link from 'next/link'
import { useState, useCallback, useEffect } from 'react'
import { FaChevronDown } from 'react-icons/fa6'
import type { Section } from 'types/section'
import { footerIcons, footerSections } from 'utils/constants'
import { ENVIRONMENT, RELEASE_VERSION } from 'utils/env.client'

export default function Footer() {
  // State to keep track of the open section in the footer
  const [openSection, setOpenSection] = useState<string | null>(null)
  // Mobile detection state
  const [isMobile, setIsMobile] = useState(false)

  // Function to toggle the section open/closed
  const toggleSection = useCallback((title: string) => {
    // If the section is already open, close it, otherwise open it
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  // Mobile detection effect
  useEffect(() => {
    const mediaQuery = globalThis.matchMedia('(max-width: 1023px)')
    setIsMobile(mediaQuery.matches)
    
    const handleChange = (e: MediaQueryListEvent) => {
      setIsMobile(e.matches)
    }
    
    mediaQuery.addEventListener('change', handleChange)
    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [])

  return (
    <footer className="mt-auto w-full border-t-1 border-t-slate-300 bg-slate-200 xl:max-w-full dark:border-t-slate-600 dark:bg-slate-800">
      <div className="grid w-full place-content-center gap-6 px-4 py-4 text-slate-800 md:py-8 dark:text-slate-200">
        <div className="grid w-full sm:grid-cols-2 sm:gap-20 md:grid-cols-4">
          {footerSections.map((section: Section) => {
            const sectionId = `footer-section-${section.title.toLowerCase().replaceAll(/\s+/g, '-')}`
            const isOpen = openSection === section.title
            
            return (
              <div key={section.title} className="flex flex-col gap-4">
                {/*link*/}
                {isMobile ? (
                  <Button
                    disableAnimation
                    onPress={() => toggleSection(section.title)}
                    className="flex w-full items-center justify-between rounded-md bg-transparent pl-0 text-left text-lg font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
                    aria-expanded={isOpen}
                    aria-controls={sectionId}
                  >
                    <h3>{section.title}</h3>
                    <div className="transition-transform duration-200">
                      <FaChevronDown 
                        className={`h-4 w-4 transition-transform duration-200 ${
                          isOpen ? 'rotate-180' : ''
                        }`} 
                      />
                    </div>
                  </Button>
                ) : (
                  <div className="pl-0 text-left text-lg font-semibold">
                    <h3>{section.title}</h3>
                  </div>
                )}
                <div
                  id={sectionId}
                  className={`grid transition-[grid-template-rows] duration-300 ease-in-out lg:grid-rows-[1fr] ${
                    isOpen ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'
                  }`}
                >
                  <div 
                    className="overflow-hidden"
                    inert={isMobile && !isOpen ? true : undefined}
                  >
                  <div className="flex flex-col gap-2 text-sm">
                    {section.links.map((link) => (
                      <div key={link.href || `span-${link.text}`} className="py-1">
                        {link.isSpan ? (
                          <span className="text-slate-600 dark:text-slate-400">{link.text}</span>
                        ) : (
                          <Link
                            className="rounded-md text-slate-600 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 dark:text-slate-400 dark:hover:text-slate-100"
                            href={link.href || '/'}
                            rel="noopener noreferrer"
                            target="_blank"
                          >
                            {link.text}
                          </Link>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Social Media Icons Section */}
        <div className="mb-0 flex flex-row justify-center gap-6">
          {footerIcons.map((social) => {
            const SocialIcon = social.icon
            return (
              <Link
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`OWASP Nest ${social.label}`}
                className="rounded-full p-2 text-slate-600 transition-colors duration-200 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 dark:text-slate-400 dark:hover:text-slate-100"
              >
                <SocialIcon className="h-4 w-4" />
              </Link>
            )
          })}
        </div>
        {/* Footer bottom section with copyright and version */}
        <div className="grid w-full place-content-center">
          <div className="flex w-full flex-col items-center gap-2 sm:flex-col sm:text-left">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              © <span id="year">{new Date().getFullYear()}</span> OWASP Nest. All rights reserved.
            </p>
            {RELEASE_VERSION && (
              <p className="text-sm text-slate-600 dark:text-slate-400">
                <Link
                  className="rounded-md text-slate-600 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 dark:text-slate-400 dark:hover:text-slate-100"
                  href={
                    ENVIRONMENT === 'production'
                      ? `https://github.com/OWASP/Nest/releases/tag/${RELEASE_VERSION}`
                      : `https://github.com/OWASP/Nest/commit/${RELEASE_VERSION.split('-').pop()}`
                  }
                  rel="noopener noreferrer"
                  target="_blank"
                >
                  <span>v{RELEASE_VERSION}</span>
                </Link>
              </p>
            )}
          </div>
        </div>
      </div>
    </footer>
  )
}