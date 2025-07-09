'use client'

import { useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useSession } from 'next-auth/react'
import { useEffect, useState } from 'react'
import {
    APPLY_AS_MENTEE,
    APPLY_AS_MENTOR,
} from 'server/queries/mentorshipQueries'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUserGraduate, faChalkboardTeacher } from '@fortawesome/free-solid-svg-icons'
import LoadingSpinner from 'components/LoadingSpinner'

const RoleApplicationPage = () => {
    const { data: session, update: updateSession, status: sessionStatus } = useSession()
    const [userRoles, setUserRoles] = useState<string[]>([])

    // ✅ Helper to extract roles from session and update state
    const updateRolesFromSession = (sessionData: any) => {
        const roles = sessionData?.user?.roles ?? []
        setUserRoles(Array.isArray(roles) ? roles : [])
    }

    // ✅ Sync on mount or session change
    useEffect(() => {
        if (sessionStatus === 'authenticated') {
            updateRolesFromSession(session)
        }
    }, [session, sessionStatus])

    const [applyAsMentee, { loading: loadingMentee }] = useMutation(APPLY_AS_MENTEE, {
        onCompleted: async (data) => {
            if (data.applyAsMentee.success) {
                addToast({
                    title: 'Success!',
                    description: 'You are now registered as a Contributor.',
                    color: 'success',
                    variant: 'solid',
                    timeout: 3000,
                })

                const updated = await updateSession()
                updateRolesFromSession(updated) // ✅ Sync roles
            } else {
                addToast({
                    title: 'Application Failed',
                    description: data.applyAsMentee.message || 'An unknown error occurred.',
                    color: 'danger',
                    variant: 'solid',
                    timeout: 5000,
                })
            }
        },
        onError: (err) => {
            addToast({
                title: 'Request Failed',
                description: err.message,
                color: 'danger',
                variant: 'solid',
                timeout: 5000,
            })
        },
    })

    const [applyAsMentor, { loading: loadingMentor }] = useMutation(APPLY_AS_MENTOR, {
        onCompleted: async (data) => {
            if (data.applyAsMentor.success) {
                addToast({
                    title: 'Success!',
                    description: 'You are now registered as a Mentor.',
                    color: 'success',
                    variant: 'solid',
                    timeout: 3000,
                })

                const updated = await updateSession()
                updateRolesFromSession(updated) // ✅ Sync roles
            } else {
                addToast({
                    title: 'Application Failed',
                    description: data.applyAsMentor.message || 'An unknown error occurred.',
                    color: 'danger',
                    variant: 'solid',
                    timeout: 5000,
                })
            }
        },
        onError: (err) => {
            addToast({
                title: 'Request Failed',
                description: err.message,
                color: 'danger',
                variant: 'solid',
                timeout: 5000,
            })
        },
    })

    const isContributor = userRoles.includes('contributor')
    const isMentor = userRoles.includes('mentor')

    if (sessionStatus === 'loading') return <LoadingSpinner />

    if (sessionStatus === 'unauthenticated') {
        return (
            <div className="flex h-64 items-center justify-center">
                <p className="text-center text-red-500">
                    You must be logged in to apply for a role.
                </p>
            </div>
        )
    }

    return (
        <div className="mx-auto max-w-4xl p-4 md:p-6">
            <div className="text-center">
                <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
                    Join the Mentorship Program
                </h1>
                <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
                    Choose how you would like to participate. You can be both a contributor and a mentor across different programs.
                </p>
            </div>

            <div className="mt-10 grid grid-cols-1 gap-8 md:grid-cols-2">
                {/* Contributor Card */}
                <div className="flex flex-col rounded-lg border p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                    <FontAwesomeIcon icon={faUserGraduate} className="h-10 w-10 text-blue-400" />
                    <h3 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
                        As a Contributor (Mentee)
                    </h3>
                    <p className="mt-2 flex-grow text-base text-gray-500 dark:text-gray-400">
                        Learn from experienced mentors, contribute to projects, and accelerate your growth.
                    </p>
                    <div className="mt-6">
                        {isContributor ? (
                            <p className="rounded-md bg-green-100 px-4 py-2 text-center font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                                You are a Contributor
                            </p>
                        ) : (
                            <button
                                onClick={() => applyAsMentee()}
                                disabled={loadingMentee}
                                className="w-full rounded-md bg-blue-600 px-4 py-2 text-base font-semibold text-white shadow-sm hover:bg-blue-500 disabled:opacity-50"
                            >
                                {loadingMentee ? <LoadingSpinner size="sm" /> : 'Apply as Contributor'}
                            </button>
                        )}
                    </div>
                </div>

                {/* Mentor Card */}
                <div className="flex flex-col rounded-lg border p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                    <FontAwesomeIcon icon={faChalkboardTeacher} className="h-10 w-10 text-purple-400" />
                    <h3 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">
                        As a Mentor
                    </h3>
                    <p className="mt-2 flex-grow text-base text-gray-500 dark:text-gray-400">
                        Guide the next generation of contributors and share your expertise. You must be a project leader to apply.
                    </p>
                    <div className="mt-6">
                        {isMentor ? (
                            <p className="rounded-md bg-green-100 px-4 py-2 text-center font-medium text-green-800 dark:bg-green-900 dark:text-green-200">
                                You are a Mentor
                            </p>
                        ) : (
                            <button
                                onClick={() => applyAsMentor()}
                                disabled={loadingMentor}
                                className="w-full rounded-md bg-purple-600 px-4 py-2 text-base font-semibold text-white shadow-sm hover:bg-purple-500 disabled:opacity-50"
                            >
                                {loadingMentor ? <LoadingSpinner size="sm" /> : 'Apply as Mentor'}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default RoleApplicationPage
