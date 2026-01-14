import DOMPurify from 'dompurify'
import markdownit from 'markdown-it'
import taskLists from 'markdown-it-task-lists'
import React from 'react'

export default function Markdown({
  content,
  className,
}: {
  content: string
  className?: string
}): React.ReactElement {
  // prettier-ignore
  const md = markdownit({  // NOSONAR - Safe to use markdown-it as we use DOMPurify to sanitize the content.
    breaks: true,
    html: true,
    linkify: true,
    typographer: true,
  }).use(taskLists)

  return (
    <div
      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(md.render(content)) }}
      className={`md-wrapper ${className}`}
    />
  )
}
