'use client'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Link from 'next/link'
import { useState, useCallback } from 'react'
import type { Section } from 'types/section'
import { footerIcons } from 'utils/constants'
import { footerSections } from 'utils/constants'
import { ENVIRONMENT, RELEASE_VERSION } from 'utils/credentials'

// Add className to props
interface FooterProps {
  className?: string
}

export default function Footer({ className }: FooterProps) {
  const [openSection, setOpenSection] = useState<string | null>(null)

  const toggleSection = useCallback((title: string) => {
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  return (
    <footer className={`w-full border-t bg-slate-200 dark:bg-slate-800 ${className || ''}`}>
      <div className="grid w-full place-content-center gap-12 px-4 py-4 text-slate-800 md:py-8 dark:text-slate-200">
        <div className="grid w-full sm:grid-cols-2 sm:gap-20 md:grid-cols-4">
          {footerSections.map((section: Section) => (
            <div key={section.title} className="space-y-4">
              <Button
                disableAnimation
                onPress={() => toggleSection(section.title)}
                className="flex w-full items-center justify-between bg-transparent pl-0 text-left text-lg font-semibold focus:ring-slate-400 focus:outline-none lg:cursor-default"
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

        {/* Footer bottom section with copyright and version */}
        <div className="grid w-full place-content-center">
          <div className="flex w-full flex-col items-center gap-2 sm:flex-col sm:text-left">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              © <span id="year">{new Date().getFullYear()}</span> OWASP Nest. All rights reserved.
            </p>
            {RELEASE_VERSION && (
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {ENVIRONMENT === 'production' ? (
                  <Link
                    className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                    href={`https://github.com/OWASP/Nest/releases/tag/${RELEASE_VERSION}`}
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    <span>v{RELEASE_VERSION}</span>
                  </Link>
                ) : (
                  <span>v{RELEASE_VERSION}</span>
                )}
              </p>
            )}
          </div>
        </div>
      </div>
    </footer>
  )
}