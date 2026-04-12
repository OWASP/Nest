import { useSession } from 'next-auth/react'
import type { ComponentProps } from 'react'
import type { ExtendedSession } from 'types/auth'
import { IS_PROJECT_HEALTH_ENABLED } from 'utils/env.client'
import { scrollToAnchor } from 'utils/scrollToAnchor'
import type { CardType } from 'components/CardDetailsPage'
import EntityActions from 'components/EntityActions'
import MetricsScoreCircle from 'components/MetricsScoreCircle'
import StatusBadge from 'components/StatusBadge'

interface CardDetailsHeaderProps {
  title?: string
  description?: string
  type: CardType
  status?: string
  setStatus?: ComponentProps<typeof EntityActions>['setStatus']
  canUpdateStatus?: boolean
  programKey?: string
  entityKey?: string
  accessLevel?: string
  admins?: Array<{ login: string }>
  mentors?: Array<{ login: string }>
  isActive?: boolean
  isArchived?: boolean
  healthMetricsData?: Array<{ score?: number }>
}

const CardDetailsHeader = ({
  title,
  description,
  type,
  status,
  setStatus,
  canUpdateStatus,
  programKey,
  entityKey,
  accessLevel,
  admins,
  mentors,
  isActive = true,
  isArchived = false,
  healthMetricsData,
}: CardDetailsHeaderProps) => {
  const { data: session } = useSession() as { data: ExtendedSession | null }

  return (
    <>
      <div className="mt-4 flex flex-row items-center">
        <div className="flex w-full items-center justify-between">
          <h1 className="text-4xl font-bold">{title || ''}</h1>
          <div className="flex items-center gap-3">
            {type === 'program' && accessLevel === 'admin' && canUpdateStatus && programKey && (
              <EntityActions
                type="program"
                programKey={programKey}
                status={status}
                setStatus={setStatus}
              />
            )}
            {type === 'module' &&
              (() => {
                if (!programKey || !entityKey) return null
                const currentUserLogin = session?.user?.login
                const isAdmin =
                  accessLevel === 'admin' &&
                  admins?.some((admin) => admin.login === currentUserLogin)
                const isMentor = mentors?.some((mentor) => mentor.login === currentUserLogin)
                return isAdmin || isMentor ? (
                  <EntityActions
                    type="module"
                    programKey={programKey}
                    moduleKey={entityKey}
                    isAdmin={isAdmin ? true : undefined}
                    isMentor={isMentor ? true : undefined}
                  />
                ) : null
              })()}
            {!isActive && <StatusBadge status="inactive" size="md" />}
            {isArchived && type === 'repository' && <StatusBadge status="archived" size="md" />}
            {IS_PROJECT_HEALTH_ENABLED &&
              type === 'project' &&
              healthMetricsData &&
              healthMetricsData.length > 0 &&
              healthMetricsData[0].score !== undefined && (
                <MetricsScoreCircle
                  score={healthMetricsData[0]?.score}
                  clickable={true}
                  onClick={() => scrollToAnchor('issues-trend')}
                />
              )}
          </div>
        </div>
      </div>
      {description && <p className="mb-6 text-xl">{description}</p>}
    </>
  )
}

export default CardDetailsHeader
