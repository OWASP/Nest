import { useQuery } from '@apollo/client'
import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { mockAboutData } from '@unit/data/mockAboutData'
import { render } from 'wrappers/testUtil'
import { toaster } from 'components/ui/toaster'
import About from 'pages/About'

jest.mock('@apollo/client', () => ({
  ...jest.requireActual('@apollo/client'),
  useQuery: jest.fn(),
}))

jest.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon" />,
}))

jest.mock('utils/aboutData', () => ({
  aboutText: [
    'This is a test paragraph about the project.',
    'This is another paragraph about the project history.',
  ],
  roadmap: [
    { title: 'Feature 1', issueLink: 'https://github.com/owasp/test/issues/1' },
    { title: 'Feature 2', issueLink: 'https://github.com/owasp/test/issues/2' },
    { title: 'Feature 3', issueLink: 'https://github.com/owasp/test/issues/3' },
  ],
  technologies: [
    {
      section: 'Backend',
      tools: {
        Python: {
          icon: `
              <svg viewBox="0 0 128 128" width="24" height="24">
              <linearGradient id="python-original-a" gradientUnits="userSpaceOnUse" x1="70.252" y1="1237.476" x2="170.659" y2="1151.089" gradientTransform="matrix(.563 0 0 -.568 -29.215 707.817)"><stop offset="0" stop-color="#9ca3af"></stop><stop offset="1" stop-color="#9ca3af"></stop></linearGradient><linearGradient id="python-original-b" gradientUnits="userSpaceOnUse" x1="209.474" y1="1098.811" x2="173.62" y2="1149.537" gradientTransform="matrix(.563 0 0 -.568 -29.215 707.817)"><stop offset="0" stop-color="#9ca3af"></stop><stop offset="1" stop-color="#9ca3af"></stop></linearGradient><path fill="url(#python-original-a)" d="M63.391 1.988c-4.222.02-8.252.379-11.8 1.007-10.45 1.846-12.346 5.71-12.346 12.837v9.411h24.693v3.137H29.977c-7.176 0-13.46 4.313-15.426 12.521-2.268 9.405-2.368 15.275 0 25.096 1.755 7.311 5.947 12.519 13.124 12.519h8.491V67.234c0-8.151 7.051-15.34 15.426-15.34h24.665c6.866 0 12.346-5.654 12.346-12.548V15.833c0-6.693-5.646-11.72-12.346-12.837-4.244-.706-8.645-1.027-12.866-1.008zM50.037 9.557c2.55 0 4.634 2.117 4.634 4.721 0 2.593-2.083 4.69-4.634 4.69-2.56 0-4.633-2.097-4.633-4.69-.001-2.604 2.073-4.721 4.633-4.721z" transform="translate(0 10.26)"></path><path fill="url(#python-original-b)" d="M91.682 28.38v10.966c0 8.5-7.208 15.655-15.426 15.655H51.591c-6.756 0-12.346 5.783-12.346 12.549v23.515c0 6.691 5.818 10.628 12.346 12.547 7.816 2.297 15.312 2.713 24.665 0 6.216-1.801 12.346-5.423 12.346-12.547v-9.412H63.938v-3.138h37.012c7.176 0 9.852-5.005 12.348-12.519 2.578-7.735 2.467-15.174 0-25.096-1.774-7.145-5.161-12.521-12.348-12.521h-9.268zM77.809 87.927c2.561 0 4.634 2.097 4.634 4.692 0 2.602-2.074 4.719-4.634 4.719-2.55 0-4.633-2.117-4.633-4.719 0-2.595 2.083-4.692 4.633-4.692z" transform="translate(0 10.26)"></path><radialGradient id="python-original-c" cx="1825.678" cy="444.45" r="26.743" gradientTransform="matrix(0 -.24 -1.055 0 532.979 557.576)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#B8B8B8" stop-opacity=".498"></stop><stop offset="1" stop-color="#7F7F7F" stop-opacity="0"></stop></radialGradient><path opacity=".444" fill="url(#python-original-c)" d="M97.309 119.597c0 3.543-14.816 6.416-33.091 6.416-18.276 0-33.092-2.873-33.092-6.416 0-3.544 14.815-6.417 33.092-6.417 18.275 0 33.091 2.872 33.091 6.417z"></path>
              </svg>
            `,
          url: 'https://www.python.org/',
        },
      },
    },
    {
      section: 'Frontend',
      tools: {
        React: {
          icon: `
              <svg viewBox="0 0 128 128" width="24" height="24">
              <g fill="#9ca3af"><circle cx="64" cy="64" r="11.4"></circle><path d="M107.3 45.2c-2.2-.8-4.5-1.6-6.9-2.3.6-2.4 1.1-4.8 1.5-7.1 2.1-13.2-.2-22.5-6.6-26.1-1.9-1.1-4-1.6-6.4-1.6-7 0-15.9 5.2-24.9 13.9-9-8.7-17.9-13.9-24.9-13.9-2.4 0-4.5.5-6.4 1.6-6.4 3.7-8.7 13-6.6 26.1.4 2.3.9 4.7 1.5 7.1-2.4.7-4.7 1.4-6.9 2.3C8.2 50 1.4 56.6 1.4 64s6.9 14 19.3 18.8c2.2.8 4.5 1.6 6.9 2.3-.6 2.4-1.1 4.8-1.5 7.1-2.1 13.2.2 22.5 6.6 26.1 1.9 1.1 4 1.6 6.4 1.6 7.1 0 16-5.2 24.9-13.9 9 8.7 17.9 13.9 24.9 13.9 2.4 0 4.5-.5 6.4-1.6 6.4-3.7 8.7-13 6.6-26.1-.4-2.3-.9-4.7-1.5-7.1 2.4-.7 4.7-1.4 6.9-2.3 12.5-4.8 19.3-11.4 19.3-18.8s-6.8-14-19.3-18.8zM92.5 14.7c4.1 2.4 5.5 9.8 3.8 20.3-.3 2.1-.8 4.3-1.4 6.6-5.2-1.2-10.7-2-16.5-2.5-3.4-4.8-6.9-9.1-10.4-13 7.4-7.3 14.9-12.3 21-12.3 1.3 0 2.5.3 3.5.9zM81.3 74c-1.8 3.2-3.9 6.4-6.1 9.6-3.7.3-7.4.4-11.2.4-3.9 0-7.6-.1-11.2-.4-2.2-3.2-4.2-6.4-6-9.6-1.9-3.3-3.7-6.7-5.3-10 1.6-3.3 3.4-6.7 5.3-10 1.8-3.2 3.9-6.4 6.1-9.6 3.7-.3 7.4-.4 11.2-.4 3.9 0 7.6.1 11.2.4 2.2 3.2 4.2 6.4 6 9.6 1.9 3.3 3.7 6.7 5.3 10-1.7 3.3-3.4 6.6-5.3 10zm8.3-3.3c1.5 3.5 2.7 6.9 3.8 10.3-3.4.8-7 1.4-10.8 1.9 1.2-1.9 2.5-3.9 3.6-6 1.2-2.1 2.3-4.2 3.4-6.2zM64 97.8c-2.4-2.6-4.7-5.4-6.9-8.3 2.3.1 4.6.2 6.9.2 2.3 0 4.6-.1 6.9-.2-2.2 2.9-4.5 5.7-6.9 8.3zm-18.6-15c-3.8-.5-7.4-1.1-10.8-1.9 1.1-3.3 2.3-6.8 3.8-10.3 1.1 2 2.2 4.1 3.4 6.1 1.2 2.2 2.4 4.1 3.6 6.1zm-7-25.5c-1.5-3.5-2.7-6.9-3.8-10.3 3.4-.8 7-1.4 10.8-1.9-1.2 1.9-2.5 3.9-3.6 6-1.2 2.1-2.3 4.2-3.4 6.2zM64 30.2c2.4 2.6 4.7 5.4 6.9 8.3-2.3-.1-4.6-.2-6.9-.2-2.3 0-4.6.1-6.9.2 2.2-2.9 4.5-5.7 6.9-8.3zm22.2 21l-3.6-6c3.8.5 7.4 1.1 10.8 1.9-1.1 3.3-2.3 6.8-3.8 10.3-1.1-2.1-2.2-4.2-3.4-6.2zM31.7 35c-1.7-10.5-.3-17.9 3.8-20.3 1-.6 2.2-.9 3.5-.9 6 0 13.5 4.9 21 12.3-3.5 3.8-7 8.2-10.4 13-5.8.5-11.3 1.4-16.5 2.5-.6-2.3-1-4.5-1.4-6.6zM7 64c0-4.7 5.7-9.7 15.7-13.4 2-.8 4.2-1.5 6.4-2.1 1.6 5 3.6 10.3 6 15.6-2.4 5.3-4.5 10.5-6 15.5C15.3 75.6 7 69.6 7 64zm28.5 49.3c-4.1-2.4-5.5-9.8-3.8-20.3.3-2.1.8-4.3 1.4-6.6 5.2 1.2 10.7 2 16.5 2.5 3.4 4.8 6.9 9.1 10.4 13-7.4 7.3-14.9 12.3-21 12.3-1.3 0-2.5-.3-3.5-.9zM96.3 93c1.7 10.5.3 17.9-3.8 20.3-1 .6-2.2.9-3.5.9-6 0-13.5-4.9-21-12.3 3.5-3.8 7-8.2 10.4-13 5.8-.5 11.3-1.4 16.5-2.5.6 2.3 1 4.5 1.4 6.6zm9-15.6c-2 .8-4.2 1.5-6.4 2.1-1.6-5-3.6-10.3-6-15.6 2.4-5.3 4.5-10.5 6-15.5 13.8 4 22.1 10 22.1 15.6 0 4.7-5.8 9.7-15.7 13.4z"></path></g>
              </svg>
            `,
          url: 'https://reactjs.org/',
        },
      },
    },
    {
      section: 'Tests',
      tools: {
        Jest: {
          icon: `
              <svg viewBox="0 0 128 128" width="24" height="24">
              <path fill="#9ca3af" d="M124.129 63.02c0-7.692-5.828-14.165-13.652-16.012L128 .113H41.16l17.563 47.043c-7.578 1.996-13.164 8.356-13.164 15.903 0 5.546 3.058 10.464 7.703 13.496-1.832 2.367-3.953 4.55-6.356 6.62-4.523 3.848-9.539 6.805-14.957 8.766-4.89-2.996-7.008-8.285-5.094-13.02 7.457-2.07 12.88-8.394 12.88-15.827 0-9.133-8.192-16.532-18.22-16.532-10.066 0-18.253 7.434-18.253 16.57 0 4.513 2.035 8.653 5.297 11.61-.286.52-.57 1.035-.856 1.59C4.973 81.438 1.875 87.207.691 93.68c-2.363 12.941 1.508 23.336 10.84 29.215 5.258 3.293 11.047 4.957 17.282 4.957 10.714 0 21.597-4.883 32.109-9.618 7.5-3.363 15.242-6.879 22.863-8.578 2.813-.629 5.746-1 8.844-1.406 6.273-.813 12.754-1.664 18.582-4.734 6.805-3.586 11.45-9.579 12.797-16.457 1.015-5.29 0-10.614-2.61-15.274a15.35 15.35 0 002.73-8.765zm-7.945 0c0 5.14-4.606 9.32-10.27 9.32s-10.27-4.18-10.27-9.32c0-1.665.489-3.254 1.344-4.622.325-.52.735-1.035 1.14-1.48a8.517 8.517 0 011.427-1.219l.043-.039c.324-.222.691-.445 1.058-.664 0 0 .04 0 .04-.039.163-.074.327-.184.492-.258.039 0 .078-.039.12-.039.165-.07.368-.144.57-.219a8.78 8.78 0 00.571-.222c.04 0 .082-.04.121-.04.164-.034.328-.109.489-.144.043 0 .125-.039.164-.039.203-.035.367-.074.57-.11h.043l.61-.113c.042 0 .12 0 .163-.035.164 0 .325-.039.489-.039h.203c.203 0 .41-.035.652-.035h.531c.16 0 .286 0 .446.035h.082c.328.04.652.074.98.149 4.645.886 8.192 4.66 8.192 9.172zM52.527 7.508h64.102l-14.711 39.387c-.61.113-1.223.296-1.832.48l-15.484-28.66L69.074 47.19c-.613-.183-1.265-.296-1.914-.406zM81.664 59.8c-.773-3.477-2.73-6.582-5.5-8.875l8.438-15.457 8.515 15.789c-2.527 2.293-4.36 5.215-5.094 8.543zM61.25 53.96c.203-.04.367-.074.57-.113h.121c.164-.035.329-.035.489-.075h.164c.164 0 .285-.035.449-.035h1.59c.16 0 .285.035.406.035.082 0 .121 0 .203.04.164.035.285.035.45.074.038 0 .081 0 .163.035.204.039.407.074.57.113h.04c.164.035.328.07.488.145.043 0 .082.039.164.039.121.035.285.074.406.148.043 0 .082.035.125.035.16.075.325.114.489.188h.039c.203.07.367.144.531.258h.04c.163.074.327.183.491.257.04 0 .04.04.078.04.164.07.286.183.45.257l.043.035c.488.333.937.704 1.382 1.075l.043.035c.407.406.813.851 1.141 1.332 1.059 1.48 1.672 3.219 1.672 5.105 0 5.141-4.606 9.317-10.27 9.317s-10.27-4.176-10.27-9.317c-.042-4.328 3.259-7.988 7.743-9.023zm-40.102-.262c5.665 0 10.27 4.18 10.27 9.32 0 5.141-4.605 9.32-10.27 9.32-5.664 0-10.27-4.179-10.27-9.32 0-5.14 4.606-9.32 10.27-9.32zm94.79 32.067c-.895 4.73-4.118 8.875-8.844 11.351-4.442 2.332-9.903 3.07-15.649 3.809-3.136.406-6.437.851-9.617 1.554-8.476 1.887-16.625 5.586-24.531 9.133-10.106 4.551-19.645 8.84-28.484 8.84-4.606 0-8.723-1.183-12.633-3.66-8.965-5.621-8.52-16.16-7.457-21.93.976-5.402 3.707-10.468 6.316-15.312.16-.297.285-.555.445-.852.899.297 1.836.52 2.813.668-1.547 7.84 2.851 15.938 11.41 19.934l1.55.738 1.669-.555c7.133-2.293 13.734-6.027 19.562-11.02 3.301-2.812 6.114-5.843 8.477-9.136.937.149 1.875.188 2.812.188 8.477 0 15.606-5.29 17.645-12.391h6.844c2.039 7.137 9.171 12.39 17.648 12.39 3.383 0 6.52-.85 9.207-2.292 1.063 2.773 1.387 5.656.817 8.543zm0 0"></path>
              </svg>
            `,
          url: 'https://jestjs.io/',
        },
        Pytest: {
          icon: `
              <svg viewBox="0 0 128 128" width="24" height="24">
              <path fill="#9ca3af" d="M31.512 30.398h61.304a3.006 3.006 0 010 6.012H31.512a3.007 3.007 0 01-3.004-3.004 3.008 3.008 0 013.004-3.008zm0 0" fill="#9ca3af"></path><path d="M32.047 24.32H44.37v2.844H32.047zm0 0" fill="#9ca3af"></path><path d="M48.168 24.32h12.324v2.844H48.168zm0 0" fill="#9ca3af"></path><path d="M64.07 24.32h12.328v2.844H64.07zm0 0" fill="#9ca3af"></path><path d="M79.91 24.32h12.324v2.844H79.91zm0 15.22h12.324v20.835H79.91zm0 0" fill="#9ca3af"></path><path d="M64.07 39.54h12.352v33.847H64.07zm0 0" fill="#9ca3af"></path><path d="M48.168 39.54h12.324v50.698H48.168zm0 0" fill="#9ca3af"></path><path d="M32.047 39.54H44.37v61.792H32.047zm0 0" fill="#9ca3af"></path>
              </svg>
            `,
          url: 'https://docs.pytest.org/',
        },
      },
    },
    {
      section: 'Tools',
      tools: {
        Ansible: {
          icon: `
              <svg viewBox="0 0 128 128" width="24" height="24">
              <path fill="#9ca3af" d="M126 64c0 34.2-27.8 62-62 62S2 98.2 2 64 29.8 2 64 2s62 27.8 62 62"></path><path fill="#fff" d="M65 39.9l16 39.6-24.1-19.1L65 39.9zm28.5 48.7L68.9 29.2c-.7-1.7-2.1-2.6-3.8-2.6-1.7 0-3.2.9-3.9 2.6L34 94.3h9.3L54 67.5l32 25.9c1.3 1 2.2 1.5 3.4 1.5 2.4 0 4.5-1.8 4.5-4.4.1-.5-.1-1.2-.4-1.9z"></path>
              </svg>
            `,
          url: 'https://www.ansible.com/',
        },
        Docker: {
          icon: `
              <svg viewBox="0 0 128 128" width="24" height="24">
              <path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M73.8 50.8h11.3v11.5h5.7c2.6 0 5.3-.5 7.8-1.3 1.2-.4 2.6-1 3.8-1.7-1.6-2.1-2.4-4.7-2.6-7.3-.3-3.5.4-8.1 2.8-10.8l1.2-1.4 1.4 1.1c3.6 2.9 6.5 6.8 7.1 11.4 4.3-1.3 9.3-1 13.1 1.2l1.5.9-.8 1.6c-3.2 6.2-9.9 8.2-16.4 7.8-9.8 24.3-31 35.8-56.8 35.8-13.3 0-25.5-5-32.5-16.8l-.1-.2-1-2.1c-2.4-5.2-3.1-10.9-2.6-16.6l.2-1.7h9.6V50.8h11.3V39.6h22.5V28.3h13.5v22.5z"></path><path fill="#9ca3af" d="M110.4 55.1c.8-5.9-3.6-10.5-6.4-12.7-3.1 3.6-3.6 13.2 1.3 17.2-2.8 2.4-8.5 4.7-14.5 4.7H18.6c-.6 6.2.5 11.9 3 16.8l.8 1.5c.5.9 1.1 1.7 1.7 2.6 3 .2 5.7.3 8.2.2 4.9-.1 8.9-.7 12-1.7.5-.2.9.1 1.1.5.2.5-.1.9-.5 1.1-.4.1-.8.3-1.3.4-2.4.7-5 1.1-8.3 1.3h-.6c-1.3.1-2.7.1-4.2.1-1.6 0-3.1 0-4.9-.1 6 6.8 15.4 10.8 27.2 10.8 25 0 46.2-11.1 55.5-35.9 6.7.7 13.1-1 16-6.7-4.5-2.7-10.5-1.8-13.9-.1z"></path><path fill="#9ca3af" d="M110.4 55.1c.8-5.9-3.6-10.5-6.4-12.7-3.1 3.6-3.6 13.2 1.3 17.2-2.8 2.4-8.5 4.7-14.5 4.7h-68c-.3 9.5 3.2 16.7 9.5 21 4.9-.1 8.9-.7 12-1.7.5-.2.9.1 1.1.5.2.5-.1.9-.5 1.1-.4.1-.8.3-1.3.4-2.4.7-5.2 1.2-8.5 1.4l-.1-.1c8.5 4.4 20.8 4.3 35-1.1 15.8-6.1 30.6-17.7 40.9-30.9-.2.1-.4.1-.5.2z"></path><path fill="#9ca3af" d="M18.7 71.8c.4 3.3 1.4 6.4 2.9 9.3l.8 1.5c.5.9 1.1 1.7 1.7 2.6 3 .2 5.7.3 8.2.2 4.9-.1 8.9-.7 12-1.7.5-.2.9.1 1.1.5.2.5-.1.9-.5 1.1-.4.1-.8.3-1.3.4-2.4.7-5.2 1.2-8.5 1.4h-.4c-1.3.1-2.7.1-4.1.1-1.6 0-3.2 0-4.9-.1 6 6.8 15.5 10.8 27.3 10.8 21.4 0 40-8.1 50.8-26H18.7v-.1z"></path><path fill="#9ca3af" d="M23.5 71.8c1.3 5.8 4.3 10.4 8.8 13.5 4.9-.1 8.9-.7 12-1.7.5-.2.9.1 1.1.5.2.5-.1.9-.5 1.1-.4.1-.8.3-1.3.4-2.4.7-5.2 1.2-8.6 1.4 8.5 4.4 20.8 4.3 34.9-1.1 8.5-3.3 16.8-8.2 24.2-14.1H23.5z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M28.4 52.7h9.8v9.8h-9.8v-9.8zm.8.8h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm3-12h9.8v9.8h-9.8v-9.8zm.9.8h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M39.6 52.7h9.8v9.8h-9.8v-9.8zm.9.8h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M50.9 52.7h9.8v9.8h-9.8v-9.8zm.8.8h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M50.9 41.5h9.8v9.8h-9.8v-9.8zm.8.8h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm3.1 10.4H72v9.8h-9.8v-9.8zm.8.8h.8v8.1H63v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M62.2 41.5H72v9.8h-9.8v-9.8zm.8.8h.8v8.1H63v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M62.2 30.2H72V40h-9.8v-9.8zm.8.8h.8v8.1H63V31zm1.5 0h.8v8.1h-.8V31zm1.4 0h.8v8.1h-.8V31zm1.5 0h.8v8.1h-.8V31zm1.5 0h.8v8.1h-.8V31zm1.5 0h.8v8.1h-.8V31z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#9ca3af" d="M73.5 52.7h9.8v9.8h-9.8v-9.8zm.8.8h.8v8.1h-.8v-8.1zm1.4 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1zm1.5 0h.8v8.1h-.8v-8.1z"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#D4EEF1" d="M48.8 78.3c1.5 0 2.7 1.2 2.7 2.7 0 1.5-1.2 2.7-2.7 2.7-1.5 0-2.7-1.2-2.7-2.7 0-1.5 1.2-2.7 2.7-2.7"></path><path fill-rule="evenodd" clip-rule="evenodd" fill="#3A4D54" d="M48.8 79.1c.2 0 .5 0 .7.1-.2.1-.4.4-.4.7 0 .4.4.8.8.8.3 0 .6-.2.7-.4.1.2.1.5.1.7 0 1.1-.9 1.9-1.9 1.9-1.1 0-1.9-.9-1.9-1.9 0-1 .8-1.9 1.9-1.9M1.1 72.8h125.4c-2.7-.7-8.6-1.6-7.7-5.2-5 5.7-16.9 4-20 1.2-3.4 4.9-23 3-24.3-.8-4.2 5-17.3 5-21.5 0-1.4 3.8-21 5.7-24.3.8-3 2.8-15 4.5-20-1.2 1.1 3.5-4.9 4.5-7.6 5.2"></path><path fill="#BFDBE0" d="M56 97.8c-6.7-3.2-10.3-7.5-12.4-12.2-2.5.7-5.5 1.2-8.9 1.4-1.3.1-2.7.1-4.1.1-1.7 0-3.4 0-5.2-.1 6 6 13.6 10.7 27.5 10.8H56z"></path><path fill="#D4EEF1" d="M46.1 89.9c-.9-1.3-1.8-2.8-2.5-4.3-2.5.7-5.5 1.2-8.9 1.4 2.3 1.2 5.7 2.4 11.4 2.9z"></path>
              </svg>
            `,
          url: 'https://www.docker.com/',
        },
      },
    },
  ],
}))

jest.mock('components/MarkdownWrapper', () => ({
  __esModule: true,
  default: ({ content }) => <div data-testid="markdown-content">{content}</div>,
}))

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}))

const mockUserData = (username) => ({
  data: { user: mockAboutData.users[username] },
  loading: false,
  error: null,
})

const mockProjectData = {
  data: { project: mockAboutData.project },
  loading: false,
  error: null,
}

const mockError = {
  error: new Error('GraphQL error'),
}

describe('About Component', () => {
  beforeEach(() => {
    toaster.create = jest.fn()
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return mockUserData('arkid15r')
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
      }
      return { loading: true }
    })
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('renders LoadingSpinner when project data is loading', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return { loading: true, data: null, error: null }
      }
      return {
        loading: false,
        data: { user: { avatarUrl: '', company: '', name: 'Dummy', location: '' } },
        error: null,
      }
    })

    render(<About />)
    await waitFor(() => {
      // Look for the element with alt text "Loading indicator"
      const spinner = screen.getAllByAltText('Loading indicator')
      expect(spinner.length).toBeGreaterThan(0)
    })
  })

  test('renders ErrorDisplay when project is null', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return { loading: false, data: { project: null }, error: null }
      }
      return {
        loading: false,
        data: { user: { avatarUrl: '', company: '', name: 'Dummy', location: '' } },
        error: null,
      }
    })
    render(<About />)
    await waitFor(() => {
      expect(screen.getByText(/Data not found/)).toBeInTheDocument()
      expect(
        screen.getByText(/Sorry, the page you're looking for doesn't exist/)
      ).toBeInTheDocument()
    })
  })

  test('triggers toaster error when GraphQL request fails for project', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return { loading: false, data: null, error: new Error('GraphQL error') }
      }
      return {
        loading: false,
        data: { user: { avatarUrl: '', company: '', name: 'Dummy', location: '' } },
        error: null,
      }
    })
    render(<About />)
    await waitFor(() => {
      expect(toaster.create).toHaveBeenCalledWith({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
      })
    })
  })

  test('renders project history correctly', async () => {
    render(<About />)

    const historySection = screen.getByText('History').closest('div')
    expect(historySection).toBeInTheDocument()

    const markdownContents = await screen.findAllByTestId('markdown-content')
    expect(markdownContents.length).toBe(2)
    expect(markdownContents[0].textContent).toBe('This is a test paragraph about the project.')
    expect(markdownContents[1].textContent).toBe(
      'This is another paragraph about the project history.'
    )
  })

  test('renders leaders section with three leaders', async () => {
    render(<About />)

    const leadersSection = screen.getByText('Leaders').closest('div')
    expect(leadersSection).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('Arkadii Yakovets')).toBeInTheDocument()
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })
  })

  test('handles leader data loading error gracefully', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: null, loading: false, error: mockError }
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText("Error loading arkid15r's data")).toBeInTheDocument()
      expect(screen.getByText('Kate Golovanova')).toBeInTheDocument()
      expect(screen.getByText('Starr Brown')).toBeInTheDocument()
    })
  })

  test('shows fallback when user data is missing', async () => {
    ;(useQuery as jest.Mock).mockImplementation((query, options) => {
      if (options?.variables?.key === 'nest') {
        return mockProjectData
      } else if (options?.variables?.key === 'arkid15r') {
        return { data: null, loading: false, error: false }
      } else if (options?.variables?.key === 'kasya') {
        return mockUserData('kasya')
      } else if (options?.variables?.key === 'mamicidal') {
        return mockUserData('mamicidal')
      }
      return { loading: true }
    })

    render(<About />)

    await waitFor(() => {
      expect(screen.getByText(/No data available for arkid15r/i)).toBeInTheDocument()
    })
  })

  test('renders top contributors section correctly', async () => {
    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('Top Contributors')).toBeInTheDocument()
      expect(screen.getByText('Contributor 1')).toBeInTheDocument()
      expect(screen.getByText('Contributor 6')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
    })
  })

  test('toggles contributors list when show more/less is clicked', async () => {
    render(<About />)
    await waitFor(() => {
      expect(screen.getByText('Contributor 6')).toBeInTheDocument()
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
    })

    const contributorsSection = screen
      .getByRole('heading', { name: /Top Contributors/i })
      .closest('div')
    const showMoreButton = within(contributorsSection!).getByRole('button', { name: /Show more/i })
    fireEvent.click(showMoreButton)

    await waitFor(() => {
      expect(screen.getByText('Contributor 7')).toBeInTheDocument()
      expect(screen.getByText('Contributor 8')).toBeInTheDocument()
    })

    const showLessButton = within(contributorsSection!).getByRole('button', { name: /Show less/i })
    fireEvent.click(showLessButton)

    await waitFor(() => {
      expect(screen.queryByText('Contributor 7')).not.toBeInTheDocument()
    })
  })

  test('renders technologies section correctly', async () => {
    render(<About />)

    const technologiesSection = screen.getByText('Technologies & Tools').closest('div')
    expect(technologiesSection).toBeInTheDocument()

    expect(screen.getByText('Backend')).toBeInTheDocument()
    expect(screen.getByText('Frontend')).toBeInTheDocument()
    expect(screen.getByText('Tests')).toBeInTheDocument()
    expect(screen.getByText('Tools')).toBeInTheDocument()

    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Jest')).toBeInTheDocument()
    expect(screen.getByText('Docker')).toBeInTheDocument()
    expect(screen.getByText('Ansible')).toBeInTheDocument()

    const pythonLink = screen.getByText('Python').closest('a')
    expect(pythonLink).toHaveAttribute('href', 'https://www.python.org/')

    const reactLink = screen.getByText('React').closest('a')
    expect(reactLink).toHaveAttribute('href', 'https://reactjs.org/')

    const jestLink = screen.getByText('Jest').closest('a')
    expect(jestLink).toHaveAttribute('href', 'https://jestjs.io/')

    const svgElements = screen.getAllByTestId('mock-icon')
    expect(svgElements.length).toBeGreaterThan(0)
  })

  test('renders roadmap correctly', async () => {
    render(<About />)

    const roadmapSection = screen.getByText('Roadmap').closest('div')
    expect(roadmapSection).toBeInTheDocument()

    const roadmapItems = within(roadmapSection).getAllByRole('listitem')
    expect(roadmapItems).toHaveLength(3)

    expect(screen.getByText('Feature 1')).toBeInTheDocument()
    expect(screen.getByText('Feature 2')).toBeInTheDocument()
    expect(screen.getByText('Feature 3')).toBeInTheDocument()

    const links = within(roadmapSection).getAllByRole('link')
    expect(links[0].getAttribute('href')).toBe('https://github.com/owasp/test/issues/1')
  })

  test('renders project stats cards correctly', async () => {
    render(<About />)

    await waitFor(() => {
      expect(screen.getByText('Contributors')).toBeInTheDocument()
      expect(screen.getByText('Issues')).toBeInTheDocument()
      expect(screen.getByText('Forks')).toBeInTheDocument()
      expect(screen.getByText('Stars')).toBeInTheDocument()
    })
  })

  test('leader card buttons open external links', async () => {
    const windowOpenSpy = jest.spyOn(window, 'open').mockImplementation(() => null)

    render(<About />)

    await waitFor(() => {
      expect(screen.getAllByText('View Profile')).toHaveLength(3)
    })

    const viewProfileButtons = screen.getAllByText('View Profile')
    fireEvent.click(viewProfileButtons[0])

    expect(windowOpenSpy).toHaveBeenCalledWith(
      '/community/users/arkid15r',
      '_blank',
      'noopener,noreferrer'
    )

    windowOpenSpy.mockRestore()
  })
})
