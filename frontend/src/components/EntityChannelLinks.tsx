import Link from 'next/link'
import {
  getEntityChannelIcon,
  getEntityChannelUrl,
  type EntityChannelLink,
} from 'utils/entityChannels'

const EntityChannelLinks = ({ channels }: { channels: EntityChannelLink[] }) => (
  <div className="inline-flex flex-wrap items-center gap-3">
    {channels.map((channel) => {
      const url = getEntityChannelUrl(channel.platform, channel.externalId)
      if (!url) {
        return null
      }

      const PlatformIcon = getEntityChannelIcon(channel.platform)

      return (
        <Link
          aria-label={`${channel.platform} channel #${channel.name}`}
          className="inline-flex items-center gap-1 text-blue-400 hover:underline"
          href={url}
          key={`${channel.platform}-${channel.externalId}`}
          rel="noopener noreferrer"
          target="_blank"
        >
          <PlatformIcon className="h-4 w-4 shrink-0 grayscale" aria-hidden="true" />
          <span>#{channel.name}</span>
        </Link>
      )
    })}
  </div>
)

export default EntityChannelLinks
