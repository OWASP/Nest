import React from 'react'
import ReactMarkdown from 'react-markdown'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeSlug from 'rehype-slug'
import remarkGfm from 'remark-gfm'

interface MarkdownWrapperProps {
  content: string
  className?: string
}
const customComponents = {
  ol: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => (
    <ol
      style={{
        listStyleType: 'decimal',
        marginLeft: '20px',
      }}
      {...props}
    >
      {children}
    </ol>
  ),
  ul: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => (
    <ul
      style={{
        listStyleType: 'circle',
        marginLeft: '20px',
      }}
      {...props}
    >
      {children}
    </ul>
  ),
}
const MarkdownWrapper = ({ content, className = '' }: MarkdownWrapperProps) => {
  return (
    <ReactMarkdown
      className={`prose prose-invert max-w-none ${className}`}
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw, rehypeSanitize, rehypeSlug]}
      components={customComponents}
    >
      {content}
    </ReactMarkdown>
  )
}

export default MarkdownWrapper
