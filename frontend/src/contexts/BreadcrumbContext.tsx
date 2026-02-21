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

const classNameStack: string[] = []
const classNameListeners = new Set<() => void>()

function notifyClassNameListeners() {
  classNameListeners.forEach((listener) => listener())
}

export function registerBreadcrumbClassName(className: string): () => void {
  classNameStack.push(className)
  notifyClassNameListeners()

  return () => {
    const index = classNameStack.lastIndexOf(className)
    if (index !== -1) classNameStack.splice(index, 1)
    notifyClassNameListeners()
  }
}

function getCurrentBreadcrumbClassName(): string {
  return classNameStack.at(-1) ?? ''
}

export function useBreadcrumbClassName(): string {
  const [className, setClassName] = useState<string>(() => getCurrentBreadcrumbClassName())

  useEffect(() => {
    const listener = () => {
      setClassName(getCurrentBreadcrumbClassName())
    }
    classNameListeners.add(listener)
    listener()

    return () => {
      classNameListeners.delete(listener)
    }
  }, [])

  return className
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

type BreadcrumbProviderProps = Readonly<{
  item: BreadcrumbItem
  children: ReactNode
}>

export function BreadcrumbProvider({ item, children }: BreadcrumbProviderProps) {
  useEffect(() => {
    const unregister = registerBreadcrumb(item)
    return unregister
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [item.path, item.title])

  return <>{children}</>
}

export function BreadcrumbRoot({ children }: Readonly<{ children: ReactNode }>) {
  useEffect(() => {
    const unregister = registerBreadcrumb({ title: 'Home', path: '/' })
    return unregister
  }, [])

  return <>{children}</>
}

type BreadcrumbStyleProviderProps = Readonly<{
  className: string
  children: ReactNode
}>

export function BreadcrumbStyleProvider({ className, children }: BreadcrumbStyleProviderProps) {
  useEffect(() => {
    const unregister = registerBreadcrumbClassName(className)
    return unregister
  }, [className])

  return <>{children}</>
}
