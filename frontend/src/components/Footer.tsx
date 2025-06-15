'use client'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Link from 'next/link'
import { useState, useCallback } from 'react'
import type { Section } from 'types/section'
import { footerIcons } from 'utils/constants'
import { footerSections } from 'utils/constants'

export default function Footer() {
  // State to keep track of the open section in the footer
  const [openSection, setOpenSection] = useState<string | null>(null)

  // Function to toggle the section open/closed
  const toggleSection = useCallback((title: string) => {
    // If the section is already open, close it, otherwise open it
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  return (
    <footer className="mt-auto w-full border-t bg-slate-200 dark:bg-slate-800 xl:max-w-full">
      <div className="grid w-full place-content-center gap-12 px-4 py-4 text-slate-800 dark:text-slate-200 md:py-8">
        <div className="grid w-full sm:grid-cols-2 sm:gap-20 md:grid-cols-4">
          {footerSections.map((section: Section) => (
            <div key={section.title} className="space-y-4">
              {/*link*/}
              <Button
                disableAnimation
                onPress={() => toggleSection(section.title)}
                className="flex w-full items-center justify-between bg-transparent pl-0 text-left text-lg font-semibold focus:outline-none focus:ring-slate-400 lg:cursor-default"
                aria-expanded={openSection === section.title}
                aria-controls={`footer-section-${section.title}`}
              >
                <h3>{section.title}</h3>
                <div className="transition-transform duration-200 lg:hidden">
                  {openSection === section.title ? (
                    <FontAwesomeIcon icon={faChevronUp} className="h-4 w-4" />
                  ) : (
                    <FontAwesomeIcon icon={faChevronDown} className="h-4 w-4" />
                  )}
                </div>
              </Button>
              <div
                id={`footer-section-${section.title}`}
                className={`space-y-2 overflow-hidden text-sm transition-all duration-300 ease-in-out lg:max-h-full ${
                  openSection === section.title ? 'max-h-96' : 'max-h-0 lg:max-h-full'
                }`}
              >
                {section.links.map((link, index) => (
                  <div key={index} className="py-1">
                    {link.isSpan ? (
                      <span className="text-slate-600 dark:text-slate-400">{link.text}</span>
                    ) : (
                      <Link
                        target="_blank"
                        className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                        href={link.href || '/'}
                      >
                        {link.text}
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Social Media Icons Section */}
        <div className="mb-0 flex justify-center space-x-6">
          {footerIcons.map((social) => (
            <Link
              key={social.label}
              href={social.href}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`OWASP Nest ${social.label}`}
              className="text-slate-600 transition-colors duration-200 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
            >
              <FontAwesomeIcon icon={social.icon} className="h-6 w-6" />
            </Link>
          ))}
        </div>
        {/* Footer bottom section with copyright and links */}
        <div className="grid w-full place-content-center">
          <div className="flex w-full flex-col items-center gap-4 sm:flex-row sm:text-left">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              © <span id="year">{new Date().getFullYear()}</span> OWASP Nest. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
