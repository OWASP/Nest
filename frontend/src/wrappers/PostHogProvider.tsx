'use client'

import { usePathname, useSearchParams } from 'next/navigation'
import posthog from 'posthog-js'
import { PostHogProvider as PHProvider, usePostHog } from 'posthog-js/react'
import React, { Suspense, useEffect } from 'react'
import { ENVIRONMENT, POSTHOG_HOST, POSTHOG_KEY } from 'utils/env.client'

const isPostHogEnabled =
  (ENVIRONMENT === 'staging' || ENVIRONMENT === 'production') && POSTHOG_KEY && POSTHOG_HOST

if (typeof window !== 'undefined' && isPostHogEnabled) {
  posthog.init(POSTHOG_KEY, {
    /* eslint-disable @typescript-eslint/naming-convention */
    api_host: POSTHOG_HOST,
    capture_pageview: false, // We capture pageviews manually
    capture_pageleave: true,
    person_profiles: 'identified_only',
    /* eslint-enable @typescript-eslint/naming-convention */
  })
}

function PostHogPageView() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const posthogClient = usePostHog()

  useEffect(() => {
    if (pathname && posthogClient) {
      let url = window.origin + pathname
      if (searchParams.toString()) {
        url = url + '?' + searchParams.toString()
      }
      // eslint-disable-next-line @typescript-eslint/naming-convention
      posthogClient.capture('$pageview', { $current_url: url })
    }
  }, [pathname, searchParams, posthogClient])

  return null
}

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  if (!isPostHogEnabled) {
    return <>{children}</>
  }

  return (
    <PHProvider client={posthog}>
      <Suspense fallback={null}>
        <PostHogPageView />
      </Suspense>
      {children}
    </PHProvider>
  )
}
