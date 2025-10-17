import { faRectangleList } from '@fortawesome/free-solid-svg-icons'
import upperFirst from 'lodash/upperFirst'
import SecondaryCard from 'components/SecondaryCard'
import AnchorTitle from 'components/AnchorTitle'
import LeadersList from 'components/LeadersList'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import SocialLinks from 'components/SocialLinks'
import type { JSX } from 'react'
import type { Chapter } from 'types/chapter'

interface DetailsSectionProps {
  details?: { label: string; value: string | JSX.Element }[]
  socialLinks?: string[]
  type: string
  geolocationData?: Chapter[]
}

const DetailsSection = ({ details, socialLinks, type, geolocationData }: DetailsSectionProps) => (
  <>
    <SecondaryCard
      icon={faRectangleList}
      title={<AnchorTitle title={`${upperFirst(type)} Details`} />}
      className={
        type === 'program' || type === 'module'
          ? 'gap-2 md:col-span-7'
          : type !== 'chapter'
            ? 'gap-2 md:col-span-5'
            : 'gap-2 md:col-span-3'
      }
    >
      {details?.map((detail) =>
        detail?.label === 'Leaders' ? (
          <div key={detail.label} className="flex flex-row gap-1 pb-1">
            <strong>{detail.label}:</strong>{' '}
            <LeadersList leaders={detail?.value != null ? String(detail.value) : 'Unknown'} />
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
    {type === 'chapter' && geolocationData && (
      <div className="mb-8 h-[250px] md:col-span-4 md:h-auto">
        <ChapterMapWrapper
          geoLocData={geolocationData}
          showLocal={true}
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
  </>
)

export default DetailsSection
