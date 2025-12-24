import DOMPurify from 'dompurify'
import markdownit from 'markdown-it'
import taskLists from 'markdown-it-task-lists'

export default function Markdown({ content, className }: { content: string; className?: string }) {
  // #NOSONAR - Safe to use markdown-it as we use DOMPurify to sanitize the content
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
