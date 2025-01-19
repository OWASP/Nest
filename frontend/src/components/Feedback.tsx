import { FeedbackForm } from './FeedbackForm'
import { Toaster } from './ui/Toaster'

export default function Feedback() {
  return (
    <>
      <main className="mx-auto my-16 h-full min-h-screen w-full max-w-lg p-4">
        <FeedbackForm />
      </main>
      <Toaster />
    </>
  )
}
