import { isGithubAuthEnabled } from 'utils/credentials'
import LoginPageContent from 'components/LoginPageContent'

export default function LoginPage() {
  return <LoginPageContent isGitHubAuthEnabled={isGithubAuthEnabled()} />
}
