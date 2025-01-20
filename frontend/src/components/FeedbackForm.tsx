import { zodResolver } from '@hookform/resolvers/zod'
import { postFeedback } from 'api/postFeedbackData'
import { useToast } from 'hooks/useToast'
import { useRef, useState } from 'react'
import ReCAPTCHA from 'react-google-recaptcha'
import { useForm } from 'react-hook-form'
import { RECAPTCHA_SITE_KEY } from 'utils/credentials'
import {
  anonymousFeedbackFormSchema,
  feedbackFormSchema,
  type FeedbackFormValues,
} from 'utils/helpers/schema'
import { Button } from 'components/ui/Button'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from 'components/ui/Form'
import { Input } from 'components/ui/Input'
import { Switch } from 'components/ui/Switch'
import { Textarea } from 'components/ui/Textarea'

export function FeedbackForm() {
  const [isAnonymous, setIsAnonymous] = useState(false)
  const { toast } = useToast()
  const captchaRef = useRef(null)

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
    const token = captchaRef.current.getValue()
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
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8 rounded-lg border border-border bg-owasp-blue p-8 dark:bg-slate-800"
      >
        <h1 className="w-full text-center font-bold">Feedback form</h1>
        {!isAnonymous && (
          <>
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Your name"
                      {...field}
                      className="border-gray-300 placeholder-gray-300 dark:border-gray-600 dark:placeholder-gray-400"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="email@example.com"
                      {...field}
                      className="border-gray-300 placeholder-gray-300 dark:border-gray-600 dark:placeholder-gray-400"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </>
        )}
        <FormField
          control={form.control}
          name="message"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Message</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Your feedback here..."
                  className="border-gray-300 placeholder-gray-300 dark:border-gray-600 dark:placeholder-gray-400"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="is_anonymous"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center justify-between gap-4 rounded-lg border border-border p-4">
              <div className="space-y-0.5">
                <FormLabel className="text-base">Anonymous Feedback</FormLabel>
              </div>
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={(checked) => {
                    field.onChange(checked)
                    setIsAnonymous(checked)
                  }}
                  className="bg-gray-300 dark:bg-gray-600"
                />
              </FormControl>
            </FormItem>
          )}
        />
        <ReCAPTCHA sitekey={RECAPTCHA_SITE_KEY} ref={captchaRef} />
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      </form>
    </Form>
  )
}
