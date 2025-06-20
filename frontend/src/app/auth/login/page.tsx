import { IS_GITHUB_AUTH_ENABLED } from 'utils/credentials'
import LoginPageContent from 'components/LoginPageContent'

export default function LoginPage() {
  return <LoginPageContent isGitHubAuthEnabled={IS_GITHUB_AUTH_ENABLED} />
}
