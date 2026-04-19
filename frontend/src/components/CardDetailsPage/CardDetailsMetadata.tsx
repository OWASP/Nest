import type { JSX } from 'react'
import { FaChartPie, FaRectangleList } from 'react-icons/fa6'
import type { Stats } from 'types/card'
import type { Chapter } from 'types/chapter'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import InfoBlock from 'components/InfoBlock'
import LeadersList from 'components/LeadersList'
import SecondaryCard from 'components/SecondaryCard'

interface CardDetailsMetadataProps {
  details?: Array<{ label: string; value: string | JSX.Element }>
  entityKey?: string
  stats?: Stats[]
  geolocationData?: Chapter[]
  socialLinks?: string[]
  showStatistics?: boolean
  showGeolocation?: boolean
  showSocialLinks?: boolean
  detailsTitle?: string
}

const CardDetailsMetadata = ({
  details,
  entityKey,
  stats,
  geolocationData = [],
  socialLinks,
  showStatistics = !!stats,
  showGeolocation = false,
  showSocialLinks = false,
  detailsTitle = 'Details',
}: CardDetailsMetadataProps) => {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
      <SecondaryCard
        icon={FaRectangleList}
        title={<AnchorTitle title={detailsTitle} />}
        className="gap-2 md:col-span-5"
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
        {showSocialLinks && socialLinks && <SocialLinks urls={socialLinks} />}
      </SecondaryCard>
      {showStatistics && stats && (
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
      {showGeolocation && geolocationData && geolocationData.length > 0 && (
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
