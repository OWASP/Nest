import Image from 'next/image'
import React from 'react'
import type { SnapshotPost } from 'types/snapshot'
import { formatDate } from 'utils/dateFormatter'

interface PostCardProps {
  post: SnapshotPost
}

const PostCard: React.FC<PostCardProps> = ({ post }) => (
  <a
    href={post.url}
    target="_blank"
    rel="noopener noreferrer"
    className="block rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
  >
    <div className="flex items-center gap-3">
      {post.authorImageUrl && (
        <Image
          src={post.authorImageUrl}
          alt={post.authorName}
          width={40}
          height={40}
          className="h-10 w-10 rounded-full"
        />
      )}
      <div>
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">{post.title}</h3>
        <div className="mt-1 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span>{post.authorName}</span>
          <span>·</span>
          <span>{formatDate(post.publishedAt)}</span>
        </div>
      </div>
    </div>
  </a>
)

export default PostCard
