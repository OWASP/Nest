import upperFirst from 'lodash/upperFirst'
import type { JSX } from 'react'
import { FaChartPie, FaRectangleList } from 'react-icons/fa6'
import type { Stats } from 'types/card'
import type { Chapter } from 'types/chapter'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import type { CardType } from 'components/CardDetailsPage'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import InfoBlock from 'components/InfoBlock'
import LeadersList from 'components/LeadersList'
import SecondaryCard from 'components/SecondaryCard'

interface CardDetailsMetadataProps {
  type: CardType
  details?: Array<{ label: string; value: string | JSX.Element }>
  entityKey?: string
  stats?: Stats[]
  geolocationData?: Chapter[]
  socialLinks?: string[]
}

const showStatistics = (type: CardType): boolean =>
  ['committee', 'organization', 'project', 'repository', 'user'].includes(type)

const CardDetailsMetadata = ({
  type,
  details,
  entityKey,
  stats,
  geolocationData = [],
  socialLinks,
}: CardDetailsMetadataProps) => {
  const secondaryCardStyles: Record<CardType, string> = {
    chapter: 'gap-2 md:col-span-3',
    committee: 'gap-2 md:col-span-5',
    module: 'gap-2 md:col-span-7',
    organization: 'gap-2 md:col-span-5',
    program: 'gap-2 md:col-span-7',
    project: 'gap-2 md:col-span-5',
    repository: 'gap-2 md:col-span-5',
    user: 'gap-2 md:col-span-5',
  }

  const typeStyles = secondaryCardStyles[type] ?? 'gap-2 md:col-span-5'

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
      <SecondaryCard
        icon={FaRectangleList}
        title={<AnchorTitle title={`${upperFirst(type)} Details`} />}
        className={typeStyles}
      >
        {details?.map((detail) =>
          detail?.label === 'Leaders' ? (
            <div key={detail.label} className="flex flex-row gap-1 pb-1">
              <strong>{detail.label}:</strong>{' '}
              <LeadersList
                entityKey={`${entityKey}-${detail.label}`}
                leaders={String(detail?.value ?? 'Unknown')}
              />
            </div>
          ) : (
            <div key={detail.label} className="pb-1">
              <strong>{detail.label}:</strong> {detail?.value || 'Unknown'}
            </div>
          )
        )}
        {socialLinks && (type === 'chapter' || type === 'committee') && (
          <SocialLinks urls={socialLinks} />
        )}
      </SecondaryCard>
      {showStatistics(type) && stats && (
        <SecondaryCard
          icon={FaChartPie}
          title={<AnchorTitle title="Statistics" />}
          className="md:col-span-2"
        >
          {stats.map((stat) => (
            <div key={`${stat.unit}-${stat.value}`}>
              <InfoBlock
                className="pb-1"
                icon={stat.icon}
                pluralizedName={stat.pluralizedName}
                unit={stat.unit}
                value={stat.value}
              />
            </div>
          ))}
        </SecondaryCard>
      )}
      {type === 'chapter' && geolocationData && geolocationData.length > 0 && (
        <div className="mb-8 h-[250px] md:col-span-4 md:h-auto">
          <ChapterMapWrapper
            geoLocData={geolocationData}
            showLocal={true}
            showLocationSharing={true}
            style={{
              borderRadius: '0.5rem',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              height: '100%',
              width: '100%',
              zIndex: '0',
            }}
          />
        </div>
      )}
    </div>
  )
}

const SocialLinks = ({ urls }: { urls: string[] }) => {
  if (!urls || urls.length === 0) return null
  return (
    <div>
      <strong>Social Links</strong>
      <div className="mt-2 flex flex-wrap gap-3">
        {urls.map((url: string) => {
          const SocialIcon = getSocialIcon(url)
          return (
            <a
              key={url}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 transition-colors hover:text-gray-800 dark:hover:text-gray-200"
              aria-label={`Link to ${url}`}
            >
              <SocialIcon className="h-5 w-5" />
            </a>
          )
        })}
      </div>
    </div>
  )
}

export default CardDetailsMetadata
