import { IS_GITHUB_AUTH_ENABLED } from 'utils/env.server'
import LoginPageContent from 'components/LoginPageContent'

export default function LoginPage() {
  return <LoginPageContent isGitHubAuthEnabled={IS_GITHUB_AUTH_ENABLED} />
}
