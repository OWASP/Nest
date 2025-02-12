import React from 'react'

export interface DefaultMetadata {
  siteName: string
  baseUrl: string
  defaultDescription: string
  twitterHandle: string
  defaultIcon: string
}

export interface PageMetadata {
  pageTitle: string
  description: string
  keywords: string[]
  image?: string
  type?: string
  url?: string
}

export interface MetadataConfig {
  home: PageMetadata
  projects: PageMetadata
  committees: PageMetadata
  chapters: PageMetadata
  users: PageMetadata
  projectContribute: PageMetadata
}

export interface MetadataManagerProps {
  pageTitle: string
  description?: string
  image?: string
  url?: string
  type?: string
  keywords?: string[]
  children?: React.ReactNode
}
