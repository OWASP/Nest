import React from 'react'

export interface DefaultMetadata {
  siteName: string
  baseUrl: string
  defaultDescription: string
  twitterHandle: string
  defaultIcon: string
  author: string
}

export interface PageMetadata {
  title: string
  description: string
  keywords: string[]
  image?: string
  type?: string
  url?: string
}

export interface MetadataManagerProps {
  title: string
  description?: string
  image?: string
  url?: string
  type?: string
  keywords?: string[]
  children?: React.ReactNode
}

export interface SEOWrapperProps extends PageMetadata {
  children: React.ReactNode
}
