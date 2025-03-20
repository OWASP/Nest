import React from 'react'

export interface DefaultMetadata {
  baseUrl: string
  defaultDescription: string
  defaultIcon: string
  siteName: string
  twitterHandle: string
}

export interface PageMetadata {
  description: string
  image?: string
  keywords: string[]
  pageTitle: string
  type?: string
  url?: string
}

export interface MetadataConfig {
  chapters: PageMetadata
  committees: PageMetadata
  home: PageMetadata
  projectContribute: PageMetadata
  projects: PageMetadata
  users: PageMetadata
  snapshot: PageMetadata
}

export interface MetadataManagerProps {
  children?: React.ReactNode
  description?: string
  image?: string
  keywords?: string[]
  pageTitle: string
  type?: string
  url?: string
}
