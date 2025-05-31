import React from 'react'
import BreadCrumbs from 'components/BreadCrumbs'

interface BreadcrumbItem {
  title: string
  href: string
}
export default function PageLayout({
  bcItems,
  children,
}: {
  bcItems: BreadcrumbItem[]
  children: React.ReactNode
}) {
  return (
    <>
      <BreadCrumbs bcItems={bcItems} />
      <main>{children}</main>
    </>
  )
}
