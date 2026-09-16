import Link from 'next/link'
import { FaLinkedinIn, FaXTwitter } from 'react-icons/fa6'

interface ShareButtonsProps {
  title: string
  url: string
}

const ShareButtons = ({ title, url }: ShareButtonsProps) => {
  const encodedUrl = encodeURIComponent(url)
  const encodedTitle = encodeURIComponent(title)

  const twitterUrl = `https://x.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`
  const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`

  return (
    <div className="flex items-center gap-2">
      <Link
        aria-label="Share on X"
        className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-gray-300 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-100"
        href={twitterUrl}
        rel="noopener noreferrer"
        target="_blank"
      >
        <FaXTwitter className="h-3.5 w-3.5" />
      </Link>
      <Link
        aria-label="Share on LinkedIn"
        className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-gray-300 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-100"
        href={linkedinUrl}
        rel="noopener noreferrer"
        target="_blank"
      >
        <FaLinkedinIn className="h-3.5 w-3.5" />
      </Link>
    </div>
  )
}

export default ShareButtons
