import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCircleInfo } from '@fortawesome/free-solid-svg-icons'
import { useRouter } from 'next/navigation'
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/env.client'
import { scrollToAnchor } from 'utils/scrollToAnchor'
import ProgramActions from 'components/ProgramActions'
import MetricsScoreCircle from 'components/MetricsScoreCircle'
import { Contributor } from 'types/contributor'
import { HealthMetricsProps } from 'types/healthMetrics'

interface HeaderSectionProps {
  title?: string
  type: string
  accessLevel?: string
  status: string
  setStatus: (status: string) => void
  canUpdateStatus?: boolean
  admins?: Contributor[]
  userLogin?: string
  router: ReturnType<typeof useRouter>
  isActive?: boolean
  healthMetricsData: HealthMetricsProps[]
  description?: string
}

const HeaderSection = ({
  title,
  type,
  accessLevel,
  status,
  setStatus,
  canUpdateStatus,
  admins,
  userLogin,
  router,
  isActive,
  healthMetricsData,
  description
}: HeaderSectionProps) => (
  <>
  <div className="mt-4 flex flex-row items-center">
    <div className="flex w-full items-center justify-between">
      <h1 className="text-4xl font-bold">{title}</h1>
      {type === 'program' && accessLevel === 'admin' && canUpdateStatus && (
        <ProgramActions status={status} setStatus={setStatus} />
      )}
      {type === 'module' &&
        accessLevel === 'admin' &&
        admins?.some((admin) => admin.login === userLogin) && (
          <button
            type="button"
            className="flex items-center justify-center gap-2 rounded-md border border-[#0D6EFD] bg-transparent px-2 py-2 text-nowrap text-[#0D6EFD] transition-all hover:bg-[#0D6EFD] hover:text-white dark:border-sky-600 dark:text-sky-600 dark:hover:bg-sky-100"
            onClick={() => router.push(`${window.location.pathname}/edit`)}
          >
            Edit Module
          </button>
        )}
      {IS_PROJECT_HEALTH_ENABLED && type === 'project' && healthMetricsData.length > 0 && (
        <MetricsScoreCircle
          score={healthMetricsData[0].score}
          clickable={true}
          onClick={() => scrollToAnchor('issues-trend')}
        />
      )}
    </div>
    {!isActive && (
      <span className="ml-4 justify-center rounded bg-red-200 px-2 py-1 text-sm text-red-800">
        Inactive
      </span>
    )}
  </div>
   {description && <p className="mb-6 text-xl">{description}</p>}
   </>
)

export default HeaderSection
