import Link from 'next/link'

const SponsorCard = ({ target, title, type }: { target: string; title: string; type: string }) => (
  <div className="rounded-lg bg-gray-100 p-6 text-center shadow-md dark:bg-gray-800">
    <h3 className="mb-4 text-2xl font-semibold">Want to become a sponsor?</h3>
    <p className="mb-6 text-gray-600 dark:text-gray-400">
      Support {title} to help grow global cybersecurity community.
    </p>
    <Link
      href={`https://owasp.org/donate/?reponame=www-${type}-${target}&title=${encodeURIComponent(title)}`}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-block rounded bg-blue-500 px-6 py-3 font-bold text-white hover:bg-blue-600"
    >
      Sponsor {title}
    </Link>
  </div>
)

export default SponsorCard
