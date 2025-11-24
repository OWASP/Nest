import { Skeleton } from '@heroui/skeleton'
import SecondaryCard from 'components/SecondaryCard'

const DetailsCardSkeleton = () => {
    return (
        <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
            <div className="mx-auto max-w-6xl">
                {/* Header */}
                <div className="mt-4 flex flex-row items-center">
                    <div className="flex w-full items-center justify-between">
                        <Skeleton className="h-10 w-1/3 rounded-lg" />
                        <div className="flex items-center gap-3">
                            <Skeleton className="h-8 w-20 rounded-full" />
                        </div>
                    </div>
                </div>

                {/* Description */}
                <Skeleton className="mb-6 mt-4 h-6 w-3/4 rounded-lg" />

                {/* Summary */}
                <SecondaryCard>
                    <div className="space-y-2">
                        <Skeleton className="h-4 w-full rounded-lg" />
                        <Skeleton className="h-4 w-5/6 rounded-lg" />
                        <Skeleton className="h-4 w-4/6 rounded-lg" />
                    </div>
                </SecondaryCard>

                {/* Details Grid */}
                <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-7">
                    <div className="gap-2 md:col-span-5">
                        <SecondaryCard title={<Skeleton className="h-6 w-32 rounded-lg" />}>
                            <div className="space-y-3">
                                {[1, 2, 3, 4].map((i) => (
                                    <Skeleton key={i} className="h-5 w-full rounded-lg" />
                                ))}
                            </div>
                        </SecondaryCard>
                    </div>
                    <div className="md:col-span-2">
                        <SecondaryCard title={<Skeleton className="h-6 w-24 rounded-lg" />}>
                            <div className="space-y-3">
                                {[1, 2, 3].map((i) => (
                                    <Skeleton key={i} className="h-12 w-full rounded-lg" />
                                ))}
                            </div>
                        </SecondaryCard>
                    </div>
                </div>

                {/* Toggleable Lists */}
                <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
                    <Skeleton className="h-12 w-full rounded-lg" />
                    <Skeleton className="h-12 w-full rounded-lg" />
                </div>

                {/* Contributors */}
                <div className="mt-8">
                    <Skeleton className="h-8 w-48 rounded-lg mb-4" />
                    <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
                        {[1, 2, 3, 4, 5, 6].map((i) => (
                            <div key={i} className="flex flex-col items-center">
                                <Skeleton className="h-16 w-16 rounded-full" />
                                <Skeleton className="mt-2 h-4 w-20 rounded-lg" />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default DetailsCardSkeleton
