'use client'
import { Button } from '@heroui/button'
import Image from 'next/image'
import Link from 'next/link'
import { useTheme } from 'next-themes'
import { useState, useCallback, useEffect } from 'react'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa6'
import type { Section } from 'types/section'
import { footerIcons, footerSections } from 'utils/constants'
import { ENVIRONMENT, RELEASE_VERSION } from 'utils/env.client'

export default function Footer() {
  const { theme } = useTheme()

  const [nestLogoSrc, setNestLogoSrc] = useState('/img/logo_light.png')
  useEffect(() => {
    setNestLogoSrc(theme === 'dark' ? '/img/logo_dark.png' : '/img/logo_light.png')
  }, [theme])

  // State to keep track of the open section in the footer
  const [openSection, setOpenSection] = useState<string | null>(null)

  // Function to toggle the section open/closed
  const toggleSection = useCallback((title: string) => {
    // If the section is already open, close it, otherwise open it
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  return (
    <footer className="mt-auto w-full border-t-1 border-t-slate-300 bg-slate-200 xl:max-w-full dark:border-t-slate-600 dark:bg-slate-800">
      <div className="grid w-full place-content-center gap-6 px-4 py-4 text-slate-800 md:py-8 dark:text-slate-200">
        <div className="grid w-full sm:grid-cols-2 sm:gap-20 md:grid-cols-4">
          {footerSections.map((section: Section) => (
            <div key={section.title} className="flex flex-col gap-4">
              {/*link*/}
              <Button
                disableAnimation
                onPress={() => toggleSection(section.title)}
                className="flex w-full items-center justify-between rounded-md bg-transparent pl-0 text-left text-lg font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 lg:cursor-default"
                aria-expanded={openSection === section.title}
                aria-controls={`footer-section-${section.title}`}
              >
                <h3>{section.title}</h3>
                <div className="transition-transform duration-200 lg:hidden">
                  {openSection === section.title ? (
                    <FaChevronUp className="h-4 w-4" />
                  ) : (
                    <FaChevronDown className="h-4 w-4" />
                  )}
                </div>
              </Button>
              <div
                id={`footer-section-${section.title}`}
                className={`flex flex-col gap-2 text-sm transition-all duration-300 ease-in-out ${
                  openSection === section.title
                    ? 'max-h-96'
                    : 'max-h-0 overflow-hidden lg:max-h-full lg:overflow-visible'
                }`}
              >
                {section.links.map((link) => {
                  const isExternal = link.href?.startsWith('http')

                  return (
                    <div key={link.href || `span-${link.text}`} className="py-1">
                      {link.isSpan ? (
                        <span className="text-slate-600 dark:text-slate-400">{link.text}</span>
                      ) : (
                        <Link
                          className="rounded-md text-slate-600 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 dark:text-slate-400 dark:hover:text-slate-100"
                          href={link.href || '/'}
                          target={isExternal ? '_blank' : undefined}
                          rel={isExternal ? 'noopener noreferrer' : undefined}
                        >
                          {link.text}
                        </Link>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
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

        {/* Logos Section */}
        <div className="flex items-center justify-center gap-6">
          <Link
            href="https://owasp.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
            aria-label="OWASP Foundation"
          >
            <Image
              src="/img/OWASP_logo.svg"
              alt="OWASP Logo"
              width={100}
              height={32}
              className="h-8 w-auto dark:invert"
            />
          </Link>

          {/* Vertical Separator */}
          <div className="h-8 w-px bg-slate-400 dark:bg-white"></div>

          <Link
            href="/"
            className="flex items-center gap-2 rounded focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
            aria-label="Nest home"
          >
            <Image src={nestLogoSrc} alt="Nest Logo" width={32} height={32} className="h-8 w-8" />
            <span className="text-lg font-semibold text-slate-800 dark:text-slate-200">Nest</span>
          </Link>
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
