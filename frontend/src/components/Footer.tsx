import { footerSections } from "../utils/constants";
import { Section } from "../utils/constants";

export default function Footer() {
  return (
    <footer className="border-t bg-slate-200 dark:bg-slate-800 w-full  ">
      <div className="container px-4 py-4 md:py-8 text-slate-800 dark:text-slate-200">
        <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-4">
          {footerSections.map((section: Section) => (
            <div key={section.title} className="space-y-4">
              <h3 className="text-lg font-semibold">{section.title}</h3>
              <ul className="space-y-2 text-sm">
                {section.links.map((link, index) => (
                  <li key={index}>
                    {link.isSpan ? (
                      <span className="text-slate-600 dark:text-slate-400">
                        {link.text}
                      </span>
                    ) : (
                      <a
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
        <div className=" pt-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:ml-[52%]">
            <p className="text-sm text-slate-600 dark:text-slate-400">
              © <span id="year">{new Date().getFullYear()}</span> OWASP Nest.
              All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}
