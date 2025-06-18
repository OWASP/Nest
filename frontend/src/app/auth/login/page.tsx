import LoginPageContent from 'LoginPageContent'

export default function LoginPage() {
  const isAuthEnabled =
    !!process.env.NEXT_SERVER_GITHUB_CLIENT_SECRET && !!process.env.NEXT_SERVER_GITHUB_CLIENT_ID

  return <LoginPageContent isAuthEnabled={isAuthEnabled} />
}
