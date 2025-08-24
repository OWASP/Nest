import { isGithubAuthEnabled } from 'utils/env.server'
import LoginPageContent from 'components/LoginPageContent'

export default function LoginPage() {
  return <LoginPageContent isGitHubAuthEnabled={isGithubAuthEnabled()} />
}
