'use client'

export function SkipLink() {
  return (
    <a
      href="#main-content"
      className={[
        'sr-only',
        'focus:not-sr-only',
        'focus:fixed',
        'focus:top-4',
        'focus:left-4',
        'focus:z-[9999]',
        'focus:px-4',
        'focus:py-2',
        'focus:bg-blue-600',
        'focus:text-white',
        'focus:rounded-md',
        'focus:font-medium',
        'focus:text-sm',
        'focus:outline-none',
        'focus:ring-2',
        'focus:ring-white',
        'focus:ring-offset-2',
        'focus:ring-offset-blue-600',
      ].join(' ')}
    >
      Skip to main content
    </a>
  )
}