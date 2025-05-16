import Link from 'next/link'

interface SponsorBannerProps {
  entityType?: 'project' | 'chapter' | 'repository'
  entityKey?: string
  entityName?: string
}

const SponsorBanner = ({
  entityType,
  entityKey,
  entityName,
}: SponsorBannerProps) => {
  const generateDonateUrl = () => {
    if (!entityType || !entityKey || !entityName) return 'https://owasp.org/donate/'

    const prefixMap = {
      project: 'www-project-',
      chapter: 'www-chapter-',
      repository: 'www-repository-',
    }

    const repoName = encodeURIComponent(`${prefixMap[entityType]}${entityKey}`)
    const formattedTitle = encodeURIComponent(`OWASP ${entityName}`)
    return `https://owasp.org/donate/?reponame=${repoName}&title=${formattedTitle}`
  }

  return (
    <div className="mb-4 text-center">
      <h3 className="mb-4 text-2xl font-semibold">
        Support This {entityType ? (entityType.charAt(0).toUpperCase() + entityType.slice(1)) : 'Project'}
      </h3>
      <p className="mb-6 text-gray-600 dark:text-gray-400">
        Your donations help maintain and improve this {entityType || 'project'}.
      </p>
      <Link
        href={generateDonateUrl()}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block rounded bg-blue-500 px-6 py-3 font-bold text-white hover:bg-blue-600"
      >
        Donate Now
      </Link>
    </div>
  )
}

export default SponsorBanner
