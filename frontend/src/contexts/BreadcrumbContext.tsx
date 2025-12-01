'use client'

import { ReactNode, useState, useEffect } from 'react'
import type { BreadcrumbItem } from 'types/breadcrumb'

type BreadcrumbRegistry = {
  items: Map<string, BreadcrumbItem>
  listeners: Set<() => void>
}

const registry: BreadcrumbRegistry = {
  items: new Map(),
  listeners: new Set(),
}

function notifyListeners() {
  registry.listeners.forEach((listener) => listener())
}

export function registerBreadcrumb(item: BreadcrumbItem): () => void {
  registry.items.set(item.path, item)
  notifyListeners()

  return () => {
    registry.items.delete(item.path)
    notifyListeners()
  }
}

export function getBreadcrumbItems(): BreadcrumbItem[] {
  const items = Array.from(registry.items.values())
  return items.sort((a, b) => {
    if (a.path === '/') return -1
    if (b.path === '/') return 1
    return a.path.length - b.path.length
  })
}

export function useBreadcrumb(): BreadcrumbItem[] {
  const [items, setItems] = useState<BreadcrumbItem[]>(() => getBreadcrumbItems())

  useEffect(() => {
    const listener = () => {
      setItems(getBreadcrumbItems())
    }
    registry.listeners.add(listener)
    listener()

    return () => {
      registry.listeners.delete(listener)
    }
  }, [])

  return items
}

type BreadcrumbProviderProps = {
  item: BreadcrumbItem
  children: ReactNode
}

export function BreadcrumbProvider({ item, children }: BreadcrumbProviderProps) {
  useEffect(() => {
    const unregister = registerBreadcrumb(item)
    return unregister
  }, [item])

  return <>{children}</>
}

export function BreadcrumbRoot({ children }: { children: ReactNode }) {
  useEffect(() => {
    const unregister = registerBreadcrumb({ title: 'Home', path: '/' })
    return unregister
  }, [])

  return <>{children}</>
}
