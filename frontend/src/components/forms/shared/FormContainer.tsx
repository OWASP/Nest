'use client'

import type React from 'react'

interface FormContainerProps {
  title: string
  children: React.ReactNode
  onSubmit: (e: React.FormEvent) => void
  containerClassName?: string
}

export const FormContainer = ({
  title,
  children,
  onSubmit,
  containerClassName,
}: FormContainerProps) => {
  return (
    <div
      className={`text-text flex min-h-screen w-full flex-col items-center justify-normal p-5 ${containerClassName || ''}`}
    >
      <div className="mb-8 text-left">
        <h1 className="mb-2 text-4xl font-bold text-gray-800 dark:text-gray-200">{title}</h1>
      </div>

      <div className="w-full max-w-4xl overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-[#212529]">
        <form onSubmit={onSubmit} noValidate>
          <div className="flex flex-col gap-8 p-8">{children}</div>
        </form>
      </div>
    </div>
  )
}
