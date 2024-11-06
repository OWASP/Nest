import { MapPin } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t bg-slate-200 dark:bg-slate-800">
      <div className="container px-4 py-4 md:py-8 text-slate-800 dark:text-slate-200">
        <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-4">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">About Nest</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Our Mission
                </a>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Team
                </a>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Careers
                </a>
              </li>
            </ul>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Contribute
                </a>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Projects
                </a>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Chapters
                </a>
              </li>
            </ul>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Community</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Committees
                </a>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Events
                </a>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Forum
                </a>
              </li>
            </ul>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Contact</h3>
            <ul className="space-y-2 text-sm">
              <li className="relative flex items-center gap-2 text-slate-600 dark:text-slate-400">
                <MapPin className="h-4 w-4 absolute left-[-20px]" />
                <span>Global Locations</span>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Support
                </a>
              </li>
              <li>
                <a className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100" href="#">
                  Contact Us
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t pt-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <a className="flex items-center gap-2 text-lg font-semibold" href="#">
                <img src="../public/owasp.png" width={60} height={60} alt="Nest Logo" />
                Nest
              </a>
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400">© 2024 Nest. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
