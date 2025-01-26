import { Textarea, Input, Button } from '@chakra-ui/react'
import { zodResolver } from '@hookform/resolvers/zod'
import { postFeedback } from 'api/postFeedbackData'
import { useToast } from 'hooks/useToast'
import { useRef, useState } from 'react'
import ReCAPTCHA from 'react-google-recaptcha'
import { Controller, useForm } from 'react-hook-form'
import { RECAPTCHA_SITE_KEY } from 'utils/credentials'
import {
  anonymousFeedbackFormSchema,
  feedbackFormSchema,
  type FeedbackFormValues,
} from 'utils/helpers/schema'
import { Switch } from 'components/ui/Switch'
import { Label } from './ui/Label'

export function FeedbackForm() {
  const [isAnonymous, setIsAnonymous] = useState(false)
  const { toast } = useToast()
  const captchaRef = useRef<ReCAPTCHA>(null)

  const form = useForm<FeedbackFormValues>({
    resolver: zodResolver(isAnonymous ? anonymousFeedbackFormSchema : feedbackFormSchema),
    defaultValues: {
      name: '',
      email: '',
      message: '',
      is_anonymous: false,
      is_nestbot: false,
    },
  })

  async function onSubmit(data: FeedbackFormValues) {
    if (isAnonymous) data.email = ''
    const token = captchaRef.current?.getValue()
    if (!token) {
      toast({
        variant: 'destructive',
        title: 'Failed to submit feedback',
        description: 'Please complete the reCAPTCHA.',
      })
    } else {
      const responseData = await postFeedback(data)
      if (responseData.ok) {
        toast({
          title: 'Feedback Submitted',
          description: 'Thank you for your feedback!',
        })
        captchaRef.current.reset()
        form.reset({
          name: '',
          email: '',
          message: '',
          is_anonymous: isAnonymous,
          is_nestbot: false,
        })
      } else {
        toast({
          variant: 'destructive',
          title: 'Failed to submit feedback',
          description: 'Please try again later.',
        })
      }
    }
  }

  return (
    <form
      onSubmit={form.handleSubmit(onSubmit)}
      className="mx-auto w-full max-w-screen-lg space-y-8 rounded-lg border p-4 py-8"
    >
      <h1 className="w-full text-center font-bold">Feedback form</h1>
      {!isAnonymous && (
        <div className="flex w-full items-center justify-between gap-4">
          <div className="">
            <Label htmlFor="name">Name</Label>
            <Input
              placeholder="Your name"
              id="name"
              className="rounded-lg border border-border p-4"
              {...form.register('name')}
            />
            {form.formState.errors.name && (
              <p className="mt-1 text-xs text-red-500">{form.formState.errors.name.message}</p>
            )}
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              placeholder="email@example.com"
              id="email"
              className="rounded-lg border border-border p-4"
              {...form.register('email')}
            />
            {form.formState.errors.email && (
              <p className="mt-1 text-xs text-red-500">{form.formState.errors.email.message}</p>
            )}
          </div>
        </div>
      )}
      <div>
        <Label htmlFor="message">Message</Label>
        <Textarea
          placeholder="Your feedback here..."
          id="message"
          className="rounded-lg border border-border p-4"
          {...form.register('message')}
        />
        {form.formState.errors.message && (
          <p className="mt-1 text-xs text-red-500">{form.formState.errors.message.message}</p>
        )}
      </div>

      <div className="flex flex-row items-center justify-between gap-4 rounded-lg border border-border p-4">
        <div className="space-y-0.5">
          <Label htmlFor="is_anonymous" className="text-base">
            Anonymous Feedback
          </Label>
        </div>
        <Controller
          name="is_anonymous"
          control={form.control}
          render={({ field: { onChange, value } }) => (
            <Switch
              checked={value}
              onCheckedChange={({ checked }: { checked: boolean }) => {
                onChange(checked)
                setIsAnonymous(checked)
              }}
            />
          )}
        />
      </div>
      <ReCAPTCHA sitekey={RECAPTCHA_SITE_KEY} ref={captchaRef} />
      <Button
        className="bg-primary p-2 px-4 text-white dark:text-gray-800"
        variant="solid"
        type="submit"
        aria-label="Submit Feedback"
        disabled={form.formState.isSubmitting}
      >
        {form.formState.isSubmitting ? 'Submitting...' : 'Submit Feedback'}
      </Button>
    </form>
  )
}
