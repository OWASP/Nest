import { getStaticMetadata } from 'utils/metaconfig'

export const metadata = getStaticMetadata('community', '/community')

export default function CommunityLayout({ children }: { children: React.ReactNode }) {
  return children
}
