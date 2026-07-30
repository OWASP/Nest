import { FaDiscord, FaGlobe, FaSlack } from 'react-icons/fa'
import {
  getEntityChannelIcon,
  getEntityChannelUrl,
  getLinkableEntityChannels,
} from 'utils/entityChannels'

describe('entityChannels utils', () => {
  test('getEntityChannelIcon returns platform-specific icons', () => {
    expect(getEntityChannelIcon('slack')).toBe(FaSlack)
    expect(getEntityChannelIcon('discord')).toBe(FaDiscord)
    expect(getEntityChannelIcon('unknown')).toBe(FaGlobe)
  })

  test('getEntityChannelUrl returns Slack archive URLs', () => {
    expect(getEntityChannelUrl('slack', 'C123')).toBe('https://owasp.slack.com/archives/C123')
    expect(getEntityChannelUrl('discord', '123')).toBeNull()
  })

  test('getEntityChannelUrl returns null for missing Slack channel ids', () => {
    expect(getEntityChannelUrl('slack', '')).toBeNull()
    expect(getEntityChannelUrl('slack', null)).toBeNull()
    expect(getEntityChannelUrl('slack', undefined)).toBeNull()
  })

  test('getLinkableEntityChannels keeps only channels with name, id, platform, and URL', () => {
    expect(
      getLinkableEntityChannels([
        { name: 'chapter-test', externalId: 'C123', platform: 'slack' },
        { name: null, externalId: 'C456', platform: 'slack' },
        { name: 'proj', externalId: 'C789', platform: 'discord' },
        { name: 'other', externalId: null, platform: 'slack' },
      ])
    ).toEqual([{ name: 'chapter-test', externalId: 'C123', platform: 'slack' }])
  })
})
