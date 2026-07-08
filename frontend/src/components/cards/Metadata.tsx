import type { JSX } from 'react'
import { FaChartPie, FaChartLine, FaRectangleList, FaStar } from 'react-icons/fa6'
import type { Stats } from 'types/card'
import type { Chapter } from 'types/chapter'
import { getSocialIcon } from 'utils/urlIconMappings'
import AnchorTitle from 'components/AnchorTitle'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import InfoBlock from 'components/InfoBlock'
import LeadersList from 'components/LeadersList'
import SecondaryCard from 'components/SecondaryCard'

interface MetadataProps {
  details?: Array<{ label: string; value: string | JSX.Element }>
  entityKey?: string
  stats?: Stats[]
  geolocationData?: Chapter[]
  socialLinks?: string[]
  showStatistics?: boolean
  showGeolocation?: boolean
  showSocialLinks?: boolean
  detailsTitle?: string
  contributionScore?: number
  tierLevel?: string
}

const Metadata = ({
  details,
  entityKey,
  stats,
  geolocationData = [],
  socialLinks,
  showStatistics = !!stats,
  showGeolocation = false,
  showSocialLinks = false,
  detailsTitle = 'Details',
  contributionScore,
  tierLevel,
}: MetadataProps) => {
  const statistics = stats ?? []
  const hasStatistics = showStatistics && statistics.length > 0
  const hasContributionInfo = contributionScore !== undefined || tierLevel !== undefined

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
      <SecondaryCard
        icon={FaRectangleList}
        title={<AnchorTitle title={detailsTitle} />}
        className={`gap-2 ${hasStatistics ? 'md:col-span-5' : 'md:col-span-7'}`}
      >
        <div
          className={`flex ${hasContributionInfo ? 'flex-col sm:flex-row sm:gap-0' : 'flex-col'}`}
        >
          <div className={hasContributionInfo ? 'flex-1 sm:pr-6' : ''}>
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
          </div>

          {hasContributionInfo && (
            <>
              <div className="my-4 border-t border-gray-300 sm:mx-0 sm:my-0 sm:border-t-0 sm:border-l dark:border-gray-600" />
              <div className="flex flex-1 flex-col justify-center gap-3 sm:pl-6">
                {contributionScore !== undefined && (
                  <div className="flex items-center gap-3">
                    <FaChartLine
                      aria-hidden="true"
                      className="h-5 w-5 text-gray-400 dark:text-gray-500"
                    />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Contribution Score</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {contributionScore.toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}
                {contributionScore !== undefined && tierLevel !== undefined && (
                  <div className="border-t border-gray-200 dark:border-gray-700" />
                )}
                {tierLevel !== undefined && (
                  <div className="flex items-center gap-3">
                    <FaStar
                      aria-hidden="true"
                      className="h-5 w-5 text-gray-400 dark:text-gray-500"
                    />
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Tier Level</p>
                      <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {tierLevel}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </SecondaryCard>
      {hasStatistics && (
        <SecondaryCard
          icon={FaChartPie}
          title={<AnchorTitle title="Statistics" />}
          className="md:col-span-2"
        >
          {statistics.map((stat) => (
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

export default Metadata
