import { footerSections } from 'utils/constants'
import { Section } from 'utils/constants'

export default function Footer() {
  return (
    <footer className="container mt-auto w-full border-t bg-slate-200 dark:bg-slate-800">
      <div className="grid w-full place-content-center gap-12 px-4 py-4 text-slate-800 md:py-8 dark:text-slate-200">
        <div className="grid w-full gap-20 sm:grid-cols-2 md:grid-cols-4">
          {footerSections.map((section: Section) => (
            <div key={section.title} className="space-y-4">
              <h3 className="text-lg font-semibold">{section.title}</h3>
              <ul className="space-y-2 text-sm">
                {section.links.map((link, index) => (
                  <li key={index}>
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
        <div className="grid w-full place-content-center">
          <div className="flex w-full flex-col items-center gap-4 sm:flex-row">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              © <span id="year">{new Date().getFullYear()}</span> OWASP Nest. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
