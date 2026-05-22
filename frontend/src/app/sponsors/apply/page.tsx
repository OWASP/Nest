'use client'
import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import React, { useState } from 'react'

import { CreateSponsorDocument } from 'types/__generated__/sponsorMutations.generated'
import SponsorForm from 'components/SponsorForm'

const SponsorApplicationPage = () => {
  const router = useRouter()
  const [createSponsor, { loading }] = useMutation(CreateSponsorDocument)

  const [formData, setFormData] = useState({
    name: '',
    website: '',
    contactEmail: '',
    message: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        name: formData.name,
        url: formData.website,
        contactEmail: formData.contactEmail,
        message: formData.message,
      }

      await createSponsor({
        variables: { input },
      })

      addToast({
        description: 'Sponsorship application submitted successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
        variant: 'solid',
      })

      router.push('/sponsors')
    } catch (err) {
      addToast({
        description:
          err instanceof Error ? err.message : 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
    }
  }

  return (
    <SponsorForm
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={loading}
      title="Apply for sponsorship"
    />
  )
}

export default SponsorApplicationPage
