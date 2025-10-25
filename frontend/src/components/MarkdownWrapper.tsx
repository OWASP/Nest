import DOMPurify from 'dompurify'
import markdownit from 'markdown-it/index.mjs'
import taskLists from 'markdown-it-task-lists'

export default function Markdown({ content, className }: { content: string; className?: string }) {
  const md = markdownit({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true,
  }).use(taskLists)

  return (
    <div
      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(md.render(content)) }}
      className={`md-wrapper ${className}`}
    />
  )
}
