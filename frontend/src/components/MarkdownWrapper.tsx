import DOMPurify from 'dompurify'
import markdownit from 'markdown-it/index.mjs'

export default function Markdown({ content, className }: { content: string; className?: string }) {
  const md = markdownit({
    html: false,
    linkify: true,
    typographer: true,
  })

  return (
    <div
      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(md.render(content)) }}
      className={`md-wrapper ${className}`}
    />
  )
}
