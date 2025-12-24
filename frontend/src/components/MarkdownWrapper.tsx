import DOMPurify from 'dompurify'
import markdownit from 'markdown-it'
import taskLists from 'markdown-it-task-lists'

export default function Markdown({ content, className }: { content: string; className?: string }) {
  // Safe to use markdown-it as we use DOMPurify to sanitize the content.
  const md = markdownit({
    breaks: true,
    html: true,
    linkify: true,
    typographer: true,
  }).use(taskLists) // NOSONAR

  return (
    <div
      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(md.render(content)) }}
      className={`md-wrapper ${className}`}
    />
  )
}
