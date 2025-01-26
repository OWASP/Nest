import { Textarea, Input, Button } from "@chakra-ui/react"
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
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from 'components/ui/Form'
import { Switch } from 'components/ui/switch'

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
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8 rounded-lg border p-4 py-8 w-full max-w-screen-lg mx-auto"
      >
        <h1 className="w-full text-center font-bold">Feedback form</h1>
        {!isAnonymous && (
          <div className="w-full flex justify-between items-center gap-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Your name"
                      className="border border-border rounded-lg p-4"
                      {...field}
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
                      className="border border-border rounded-lg p-4"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
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
                  className="border border-border rounded-lg p-4"
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
                  onCheckedChange={({ checked }: { checked: boolean }) => {
                    field.onChange(checked)
                    setIsAnonymous(checked)
                  }}
                />
              </FormControl>
            </FormItem>
          )}
        />
        <ReCAPTCHA sitekey={RECAPTCHA_SITE_KEY} ref={captchaRef} />
        <Button className="p-2 px-4 bg-primary text-white dark:text-gray-800" variant='solid' type="submit" aria-label="Submit Feedback" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      </form>
    </Form>
  )
}
