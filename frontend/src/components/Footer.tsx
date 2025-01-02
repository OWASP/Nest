import { ChevronDown, ChevronUp } from 'lucide-react'
import { useState, useCallback } from 'react'
import { footerSections, Section } from '../utils/constants'

export default function Footer() {
  // State to keep track of the open section in the footer
  const [openSection, setOpenSection] = useState<string | null>(null)

  // Function to toggle the section open/closed
  const toggleSection = useCallback((title: string) => {
    // If the section is already open, close it, otherwise open it
    setOpenSection((prev) => (prev === title ? null : title))
  }, [])

  return (
    <footer className="w-full border-t bg-slate-200 dark:bg-slate-800">
      <div className="container px-4 py-8 text-slate-800 dark:text-slate-200">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Iterate over footerSections to render each section */}
          {footerSections.map((section: Section) => (
            <div key={section.title} className="space-y-4">
              <button
                onClick={() => toggleSection(section.title)}
                className="flex w-full items-center justify-between text-left text-lg font-semibold focus:outline-none focus:ring-2 focus:ring-slate-400 lg:cursor-default lg:focus:ring-0"
                aria-expanded={openSection === section.title}
                aria-controls={`footer-section-${section.title}`}
              >
                <h3>{section.title}</h3>
                {/* Icon to indicate open/close state */}
                <span className="transition-transform duration-200 lg:hidden">
                  {openSection === section.title ? (
                    <ChevronUp className="h-5 w-5" />
                  ) : (
                    <ChevronDown className="h-5 w-5" />
                  )}
                </span>
              </button>
              <ul
                id={`footer-section-${section.title}`}
                className={`space-y-2 overflow-hidden text-sm transition-all duration-300 ease-in-out lg:max-h-full ${
                  openSection === section.title ? 'max-h-96' : 'max-h-0 lg:max-h-full'
                }`}
              >
                {/* Iterate through section links */}
                {section.links.map((link, index) => (
                  <li key={index} className="py-1">
                    {link.isSpan ? (
                      <span className="text-slate-600 dark:text-slate-400">{link.text}</span>
                    ) : (
                      <a
                        target="_blank"
                        className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                        href={link.href}
                      >
                        {link.text}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        {/* Footer bottom section with copyright and links */}
        <div className="mt-8 border-t border-slate-300 pt-8 dark:border-slate-700">
          <div className="flex flex-col items-center justify-between gap-4 text-center sm:flex-row sm:text-left">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              © <span id="year">{new Date().getFullYear()}</span> OWASP Nest. All rights reserved.
            </p>
            <div className="flex space-x-4">
              {/* Privacy policy and Terms of Service links */}
              <a
                href="#"
                className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
              >
                Privacy Policy
              </a>
              <a
                href="#"
                className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
              >
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
