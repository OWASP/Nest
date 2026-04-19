import type { ContributionStats as ContributionStatsType } from 'utils/contributionDataUtils'
import ContributionHeatmap from 'components/ContributionHeatmap'
import ContributionStats from 'components/ContributionStats'

interface CardDetailsContributionsProps {
  hasContributions: boolean
  contributionStats?: ContributionStatsType
  contributionData?: Record<string, number>
  startDate?: string
  endDate?: string
  title?: string
}

const CardDetailsContributions = ({
  hasContributions,
  contributionStats,
  contributionData,
  startDate,
  endDate,
  title = 'Contribution Activity',
}: CardDetailsContributionsProps) => {
  if (!hasContributions) {
    return null
  }

  return (
    <div className="mb-8">
      <div className="rounded-lg bg-gray-100 px-4 pt-6 shadow-md sm:px-6 lg:px-10 dark:bg-gray-800">
        {contributionStats && <ContributionStats title={title} stats={contributionStats} />}
        {contributionData && Object.keys(contributionData).length > 0 && startDate && endDate && (
          <div className="flex w-full items-center justify-center">
            <div className="w-full">
              <ContributionHeatmap
                contributionData={contributionData}
                startDate={startDate}
                endDate={endDate}
                unit="contribution"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CardDetailsContributions
