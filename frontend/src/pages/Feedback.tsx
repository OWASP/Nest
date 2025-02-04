import { FeedbackForm } from 'components/FeedbackForm'
import { Toaster } from 'components/ui/Toaster'

export default function FeedbackPage() {
  return (
    <>
      <main className="mx-auto my-16 h-full min-h-screen w-full max-w-lg p-4">
        <FeedbackForm />
      </main>
      <Toaster />
    </>
  )
}
