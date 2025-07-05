import { redirect } from 'next/navigation'
import { getServerSession } from 'next-auth'
import { IS_GITHUB_AUTH_ENABLED } from 'utils/credentials'
import ApiKeyPageContent from 'components/ApiKeyPageContent'

export default async function ApiKeysPage() {
  const session = await getServerSession()

  if (!session) {
    redirect('/auth/login')
  }

  return <ApiKeyPageContent isGitHubAuthEnabled={IS_GITHUB_AUTH_ENABLED} />
}
