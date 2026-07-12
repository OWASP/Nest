import type { IconType } from 'react-icons'
import { FaDiscord, FaGlobe, FaSlack } from 'react-icons/fa'
import { getSlackChannelUrl } from 'utils/urlFormatter'

export type EntityChannelLink = {
  externalId: string
  name: string
  platform: string
}

export const getEntityChannelIcon = (platform: string): IconType => {
  switch (platform.toLowerCase()) {
    case 'discord':
      return FaDiscord
    case 'slack':
      return FaSlack
    default:
      return FaGlobe
  }
}

export const getEntityChannelUrl = (platform: string, externalId: string): string | null => {
  switch (platform.toLowerCase()) {
    case 'slack':
      return getSlackChannelUrl(externalId)
    default:
      return null
  }
}

export const getLinkableEntityChannels = (
  channels:
    | Array<{
        name?: string | null
        externalId?: string | null
        platform?: string | null
      }>
    | null
    | undefined
): EntityChannelLink[] =>
  (channels ?? []).flatMap((channel) => {
    if (!channel.name || !channel.externalId || !channel.platform) {
      return []
    }

    if (!getEntityChannelUrl(channel.platform, channel.externalId)) {
      return []
    }

    return [
      {
        name: channel.name,
        externalId: channel.externalId,
        platform: channel.platform,
      },
    ]
  })
