import { ErrorDisplay } from 'app/global-error'

export default function NotFound() {
  return (
    <ErrorDisplay
      statusCode={404}
      title="Page Not Found"
      message="Sorry, the page you're looking for doesn't exist."
    />
  )
}
