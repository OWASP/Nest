import * as fs from 'fs'
import * as path from 'path'
import { ApolloClient, InMemoryCache } from '@apollo/client/core'
import { gql } from 'graphql-tag'

const SITE_URL = 'https://nest.owasp.dev'
const GraphqlURI = 'http://localhost:8000/graphql/'

const client = new ApolloClient({
  uri: GraphqlURI,
  cache: new InMemoryCache(),
})

const staticRoutes: { path: string; changefreq: string; priority: number }[] = [
  { path: '/projects', changefreq: 'daily', priority: 0.9 },
  { path: '/projects/contribute', changefreq: 'monthly', priority: 0.6 },
  { path: '/committees', changefreq: 'weekly', priority: 0.8 },
  { path: '/chapters', changefreq: 'weekly', priority: 0.8 },
  { path: '/community/users', changefreq: 'daily', priority: 0.7 },
]

const GET_ALL_ENTITY_KEYS = gql`
  query GetAllEntityKeys {
    getAllEntityKeys {
      projects
      chapters
      committees
      users
    }
  }
`

interface EntityKeys {
  getAllEntityKeys: {
    projects: string[]
    chapters: string[]
    committees: string[]
    users: string[]
  }
}

async function generateSitemap() {
  try {
    const { data } = await client.query<EntityKeys>({ query: GET_ALL_ENTITY_KEYS })

    if (!data || !data.getAllEntityKeys) {
      throw new Error(' No data received from GraphQL API')
    }

    const { projects, chapters, committees, users } = data.getAllEntityKeys

    const dynamicRoutes = [
      ...projects.map((key) => ({ path: `/projects/${key}`, changefreq: 'weekly', priority: 0.7 })),
      ...chapters.map((key) => ({ path: `/chapters/${key}`, changefreq: 'weekly', priority: 0.7 })),
      ...committees.map((key) => ({
        path: `/committees/${key}`,
        changefreq: 'weekly',
        priority: 0.7,
      })),
      ...users.map((key) => ({
        path: `/community/users/${key}`,
        changefreq: 'weekly',
        priority: 0.7,
      })),
    ]

    const lastmod = new Date().toISOString().split('T')[0]

    const sitemapContent = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${[...staticRoutes, ...dynamicRoutes]
  .map(
    (route) => `  <url>
    <loc>${SITE_URL}${route.path}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>${route.changefreq}</changefreq>
    <priority>${route.priority}</priority>
  </url>`
  )
  .join('\n')}
</urlset>`

    const publicDir = path.join(process.cwd(), 'public')
    if (!fs.existsSync(publicDir)) {
      fs.mkdirSync(publicDir, { recursive: true })
    }

    fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), sitemapContent)
  } catch (error) {
    throw new Error(` Error generating sitemap: ${error}`)
  }
}

generateSitemap().catch((error) => {
  throw new Error(` Error generating sitemap: ${error}`)
})
