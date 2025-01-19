import * as z from 'zod'

export const feedbackFormSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Enter a valid email'),
  message: z.string().min(1, 'Message is required'),
  is_anonymous: z.boolean(),
  is_nestbot: z.boolean().default(false),
})

export const anonymousFeedbackFormSchema = feedbackFormSchema.extend({
  name: z.string().optional(),
  email: z.string().optional(),
})

export type FeedbackFormValues = z.infer<typeof feedbackFormSchema>
