'use client'

import { usePathname, useSearchParams } from 'next/navigation'
import posthog from 'posthog-js'
import { PostHogProvider as PHProvider, usePostHog } from 'posthog-js/react'
import React, { Suspense, useEffect, useRef } from 'react'
import { ENVIRONMENT, POSTHOG_HOST, POSTHOG_KEY } from 'utils/env.client'

const isPostHogEnabled =
  (ENVIRONMENT === 'staging' || ENVIRONMENT === 'production') &&
  POSTHOG_KEY &&
  POSTHOG_HOST

function PostHogPageView() {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const posthogClient = usePostHog()

  useEffect(() => {
    if (pathname && posthogClient && globalThis.window !== undefined) {
      let url = globalThis.window.location.origin + pathname
      if (searchParams.toString()) {
        url += `?${searchParams.toString()}`
      }
      posthogClient.capture('$pageview', { $current_url: url })
    }
  }, [pathname, searchParams, posthogClient])

  return null
}

export function PostHogProvider({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const initialized = useRef(false)

  if (!isPostHogEnabled) {
    return <>{children}</>
  }

  if (!initialized.current && globalThis.window !== undefined) {
    posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      capture_pageview: false,
      capture_pageleave: true,
      person_profiles: 'identified_only',
    })
    initialized.current = true
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
