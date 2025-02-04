import { toast } from 'hooks/useToast'
import { API_URL } from 'utils/credentials'
import { FeedbackFormValues } from 'utils/helpers/schema'
import logger from 'utils/logger'

export const postFeedback = async (data: FeedbackFormValues) => {
  const url = `${API_URL}/feedback/`
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
