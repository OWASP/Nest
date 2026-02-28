'use client'

import { useState } from "react"
import Link from "next/link"
import { footerSections } from "../utils/constants"

export default function Footer() {
  const [openSection, setOpenSection] = useState<number | null>(null)

  const toggleSection = (index: number) => {
    setOpenSection(openSection === index ? null : index)
  }

  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="max-w-7xl mx-auto px-6 py-10">

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {footerSections.map((section, index) => (
            <div key={index}>

              {/* Section title */}
              <button
                onClick={() => toggleSection(index)}
                className="flex w-full items-center justify-between bg-transparent pl-0 text-left text-lg font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-slate-500"
              >
                {section.title}
              </button>

              {/* Links */}
              <ul
                className={`mt-3 space-y-2 ${
                  openSection === index ? "block" : "hidden md:block"
                }`}
              >
                {section.links.map((link, i) => (
                  <li key={i}>
                    <Link
                      href={link.href}
                      className="text-slate-600 hover:text-slate-900"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>

            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="mt-10 text-sm text-slate-500 text-center">
          © {new Date().getFullYear()} OWASP Nest. All rights reserved.
        </div>

      </div>
    </footer>
  )
}