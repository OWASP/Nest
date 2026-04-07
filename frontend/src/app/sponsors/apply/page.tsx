'use client'

import SponsorApplicationForm from 'components/sponsors/SponsorApplicationForm'

const SponsorApplyPage = () => {
  return (
    <div className="min-h-screen w-full flex-1 px-8 pb-8 pt-0 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-4xl">
        <SponsorApplicationForm />
      </div>
    </div>
  )
}

export default SponsorApplyPage
