'use client'

import SponsorApplicationForm from 'components/sponsors/SponsorApplicationForm'
import SponsorApplyHero from 'components/sponsors/SponsorApplyHero'

const SponsorApplyPage = () => {
  return (
    <div className="min-h-screen w-full flex-1 px-8 pt-0 pb-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <SponsorApplyHero />

        <div className="mx-auto max-w-3xl">
          <SponsorApplicationForm />
        </div>
      </div>
    </div>
  )
}

export default SponsorApplyPage
