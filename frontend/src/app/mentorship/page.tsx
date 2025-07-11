'use client'

import { useMutation } from '@apollo/client'
import {
  faUserGraduate,
  faChalkboardTeacher,
  IconDefinition,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { addToast } from '@heroui/toast'
import { useUserRoles, GET_USER_ROLES } from 'hooks/useUserRoles'
import { useSession } from 'next-auth/react'
import { APPLY_AS_MENTEE, APPLY_AS_MENTOR } from 'server/queries/mentorshipQueries'
import LoadingSpinner from 'components/LoadingSpinner'

const RoleApplicationPage = () => {
  const { status: sessionStatus } = useSession()
  const { roles, isLoadingRoles } = useUserRoles()

  const [applyAsMentee, { loading: loadingMentee }] = useMutation(APPLY_AS_MENTEE, {
    refetchQueries: [{ query: GET_USER_ROLES }],
    onCompleted: (data) => {
      const res = data?.applyAsMentee
      addToast({
        title: res?.success ? 'Success!' : 'Application Failed',
        description:
          res?.message || (res?.success ? 'You are now a Contributor.' : 'Unknown error'),
        color: res?.success ? 'success' : 'danger',
        variant: 'solid',
        timeout: 4000,
      })
    },
    onError: (err) =>
      addToast({
        title: 'Request Failed',
        description: err.message,
        color: 'danger',
        variant: 'solid',
        timeout: 5000,
      }),
  })

  const [applyAsMentor, { loading: loadingMentor }] = useMutation(APPLY_AS_MENTOR, {
    refetchQueries: [{ query: GET_USER_ROLES }],
    onCompleted: (data) => {
      const res = data?.applyAsMentor
      addToast({
        title: res?.success ? 'Success!' : 'Application Failed',
        description: res?.message || (res?.success ? 'You are now a Mentor.' : 'Unknown error'),
        color: res?.success ? 'success' : 'danger',
        variant: 'solid',
        timeout: 4000,
      })
    },
    onError: (err) =>
      addToast({
        title: 'Request Failed',
        description: err.message,
        color: 'danger',
        variant: 'solid',
        timeout: 5000,
      }),
  })

  const isContributor = roles.includes('contributor')
  const isMentor = roles.includes('mentor')

  if (sessionStatus === 'loading') return <LoadingSpinner />

  if (sessionStatus === 'unauthenticated') {
    return (
      <div className="flex h-64 min-h-[60vh] items-center justify-center">
        <p className="text-center text-gray-900 dark:text-white">
          You must be logged in to apply for a role.
        </p>
      </div>
    )
  }

  return (
    <div className="mx-auto min-h-[60vh] max-w-4xl px-4 py-12">
      <h1 className="text-center text-4xl font-extrabold text-gray-900 dark:text-gray-300">
        Apply to Join the Mentorship Program
      </h1>

      <p className="mx-auto mt-4 max-w-2xl text-center text-base text-gray-600 dark:text-gray-300">
        Whether you're just getting started or you're ready to guide others — you can be part of our
        open-source mentorship journey. Choose a role below that suits your interests and
        experience.
      </p>

      {isLoadingRoles ? (
        <div className="mt-16 flex justify-center">
          <LoadingSpinner />
        </div>
      ) : (
        <div className="mt-12 grid grid-cols-1 gap-8 md:grid-cols-2">
          <RoleCard
            icon={faUserGraduate}
            title="Contributor"
            description="Learn from experienced mentors, collaborate on real-world open source projects, and build your portfolio with meaningful work."
            isApplied={isContributor}
            onApply={applyAsMentee}
            loading={loadingMentee}
            color="blue"
          />

          <RoleCard
            icon={faChalkboardTeacher}
            title="Mentor"
            description="Support contributors, grow leadership skills, and help shape the next generation of open source developers. Must be a project maintainer or experienced contributor."
            isApplied={isMentor}
            onApply={applyAsMentor}
            loading={loadingMentor}
            color="purple"
          />
        </div>
      )}
    </div>
  )
}

const MiniSpinner = () => (
  <div className="animate-spin inline-block h-4 w-4 rounded-full border-2 border-white border-t-transparent" />
)

const RoleCard = ({
  icon,
  title,
  description,
  isApplied,
  onApply,
  loading,
  color,
}: {
  icon: IconDefinition
  title: 'Contributor' | 'Mentor'
  description: string
  isApplied: boolean
  onApply: () => void
  loading: boolean
  color: 'blue' | 'purple'
}) => {
  return (
    <div className="rounded-xl border border-gray-300 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-center gap-3">
        <FontAwesomeIcon icon={icon} className={`h-8 w-8 text-${color}-500`} />
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Apply as {title}</h2>
      </div>
      <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">{description}</p>
      <div className="mt-4">
        {isApplied ? (
          <div className="rounded-md bg-green-100 px-4 py-2 text-center text-sm font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
            You are already a {title}
          </div>
        ) : (
          <button
            onClick={onApply}
            disabled={loading}
            className={`w-full rounded-md bg-${color}-600 hover:bg-${color}-500 flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50`}
          >
            {loading ? <MiniSpinner /> : `Apply as ${title}`}
          </button>
        )}
      </div>
    </div>
  )
}

export default RoleApplicationPage
