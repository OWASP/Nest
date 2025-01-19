import { zodResolver } from '@hookform/resolvers/zod'
import { useToast } from 'hooks/useToast'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { API_URL } from 'utils/credentials'
import {
  anonymousFeedbackFormSchema,
  feedbackFormSchema,
  type FeedbackFormValues,
} from 'utils/helpers/schema'
import logger from 'utils/logger'
import { Button } from 'components/ui/button'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from 'components/ui/form'
import { Input } from 'components/ui/input'
import { Switch } from 'components/ui/switch'
import { Textarea } from 'components/ui/textarea'

export function FeedbackForm() {
  const [isAnonymous, setIsAnonymous] = useState(false)
  const { toast } = useToast()

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

  const postFeedback = async (data: FeedbackFormValues) => {
    const url = `${API_URL}/owasp/feedback/`
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error(`Failed to submit feedback: ${response.statusText}`)
      }

      return response
    } catch (error) {
      logger.error('Failed to submit feedback', error)
      toast({
        variant: 'destructive',
        title: 'Failed to submit feedback',
        description: 'Please try again later.',
      })
    }
  }

  async function onSubmit(data: FeedbackFormValues) {
    if (isAnonymous) data.email = ''

    const responseData = await postFeedback(data)
    logger.log('Feedback submitted', responseData)
    toast({
      title: 'Feedback Submitted',
      description: 'Thank you for your feedback!',
    })
    form.reset({
      name: '',
      email: '',
      message: '',
      is_anonymous: isAnonymous,
      is_nestbot: false,
    })
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
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? 'Submitting...' : 'Submit Feedback'}
        </Button>
      </form>
    </Form>
  )
}
