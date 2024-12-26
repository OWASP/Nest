import DOMPurify from 'dompurify'
import markdownit from 'markdown-it'
import React from 'react'

export default function Markdown({ content, className }: { content: string; className?: string }) {
  const md = markdownit({
    html: true,
    linkify: true,
    typographer: true,
  })

  const rawHtml = md.render(content)

  // Sanitize the HTML
  const safeHtml = DOMPurify.sanitize(rawHtml)

  return <div dangerouslySetInnerHTML={{ __html: safeHtml }} className={className} />
}
