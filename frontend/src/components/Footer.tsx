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

  const hasSocialSection = footerSections.some((section) =>
    section.title.toLowerCase().startsWith('social')
  )

  const normalizedFooterSections = footerSections

  return (
    <footer className="mt-auto w-full border-t-1 border-t-slate-300 bg-slate-200 xl:max-w-full dark:border-t-slate-600 dark:bg-slate-800">
      <div className="w-full px-10 py-4 text-slate-800 md:px-8 md:py-8 dark:text-slate-200">
        <div className="mx-auto grid w-full max-w-6xl gap-6">
          <div className="grid w-full sm:grid-cols-2 sm:gap-x-8 sm:gap-y-6 md:grid-cols-[repeat(5,max-content)] md:justify-between md:gap-x-8 lg:gap-x-8">
            {normalizedFooterSections.map((section: Section) => (
              <div key={section.title} className="flex flex-col gap-4 pl-2">
                {/*link*/}
                <Button
                  disableAnimation
                  onPress={() => toggleSection(section.title)}
                  className="flex w-full items-center justify-between rounded-md bg-transparent pl-0 text-left text-lg font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 md:justify-start md:gap-2 lg:cursor-default"
                  aria-expanded={openSection === section.title}
                  aria-controls={`footer-section-${section.title}`}
                >
                  <h3>{section.title}</h3>
                  {openSection === section.title ? (
                    <FaChevronUp className="h-4 w-4 transition-transform duration-200 lg:hidden" />
                  ) : (
                    <FaChevronDown className="h-4 w-4 transition-transform duration-200 lg:hidden" />
                  )}
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
                    const isSocialSection = section.title.toLowerCase().startsWith('social')
                    const social = isSocialSection
                      ? footerIcons.find((icon) => icon.label === link.text)
                      : undefined
                    const SocialIcon = social?.icon

                    return (
                      <div key={link.href || `span-${link.text}`} className="">
                        {link.isSpan ? (
                          <span className="text-slate-600 dark:text-slate-400">{link.text}</span>
                        ) : isSocialSection ? (
                          <a
                            className="flex items-center gap-2 rounded-md py-0.5 text-slate-600 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 dark:text-slate-400 dark:hover:text-slate-100"
                            href={link.href || '/'}
                            target={isExternal ? '_blank' : undefined}
                            rel={isExternal ? 'noopener noreferrer' : undefined}
                            aria-label={`OWASP Nest ${link.text}`}
                          >
                            {SocialIcon && <SocialIcon className="h-4 w-4" />}
                            <span>{link.text}</span>
                          </a>
                        ) : (
                          <Link
                            className="flex items-center gap-2 rounded-md py-0.5 text-slate-600 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 dark:text-slate-400 dark:hover:text-slate-100"
                            href={link.href || '/'}
                            target={isExternal ? '_blank' : undefined}
                            rel={isExternal ? 'noopener noreferrer' : undefined}
                          >
                            <span>{link.text}</span>
                          </Link>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
            {!hasSocialSection && (
              <div className="flex flex-col gap-4 pl-2">
                <h3>Socials</h3>
                <div className="flex flex-col gap-2 text-sm">
                  {footerIcons.map((social) => {
                    const SocialIcon = social.icon

                    return (
                      <div key={social.label} className="">
                        <a
                          className="flex items-center gap-2 rounded-md py-0.5 text-slate-600 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 dark:text-slate-400 dark:hover:text-slate-100"
                          href={social.href}
                          target="_blank"
                          rel="noopener noreferrer"
                          aria-label={`OWASP Nest ${social.label}`}
                        >
                          <SocialIcon className="h-4 w-4" />
                          {social.label}
                        </a>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
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
              <Image
                src={nestLogoSrc}
                alt="Nest Logo"
                width={28}
                height={32}
                className="h-8 w-auto"
              />
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
      </div>
    </footer>
  )
}
