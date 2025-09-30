import { CodegenConfig } from '@graphql-codegen/cli'

const PUBLIC_API_URL = process.env.PUBLIC_API_URL || 'http://localhost:8000'

export default (async (): Promise<CodegenConfig> => {
  let csrfToken: string | undefined
  let backendUp = false

  // Detect if backend is reachable
  try {
    const statusRes = await fetch(`${PUBLIC_API_URL}/status/`, { method: 'GET' })
    backendUp = statusRes.ok
  } catch {
    backendUp = false
  }

  if (backendUp) {
    try {
      const response = await fetch(`${PUBLIC_API_URL}/csrf/`, { method: 'GET' })
      if (response.ok) {
        csrfToken = (await response.json()).csrftoken
      }
    } catch {
      // If CSRF fails but backend is up, proceed without CSRF headers
    }
  }

  const fallbackSchemaSDL = `
    schema { query: Query }
    scalar DateTime
    scalar UUID


    """
    Minimal offline schema to allow GraphQL Codegen when backend is unavailable.
    Only includes types used by unit tests and common queries.
    """

    type Query {
      _placeholder: Boolean
      projectHealthStats: ProjectHealthStats!
      projectHealthMetrics(
        filters: ProjectHealthMetricsFilter!
        pagination: OffsetPaginationInput!
        ordering: [ProjectHealthMetricsOrder!]
      ): [ProjectHealthMetric!]!
      projectHealthMetricsDistinctLength(filters: ProjectHealthMetricsFilter!): Int!
      project(key: String!): Project
    }

    type ProjectHealthStats {
      averageScore: Float!
      monthlyOverallScores: [Float!]!
      monthlyOverallScoresMonths: [String!]!
      projectsCountHealthy: Int!
      projectsCountNeedAttention: Int!
      projectsCountUnhealthy: Int!
      projectsPercentageHealthy: Float!
      projectsPercentageNeedAttention: Float!
      projectsPercentageUnhealthy: Float!
      totalContributors: Int!
      totalForks: Int!
      totalStars: Int!
    }

    type ProjectHealthMetric {
      id: ID!
      createdAt: String
      contributorsCount: Int
      forksCount: Int
      openIssuesCount: Int
      openPullRequestsCount: Int
      recentReleasesCount: Int
      starsCount: Int
      totalIssuesCount: Int
      totalReleasesCount: Int
      unassignedIssuesCount: Int
      unansweredIssuesCount: Int
      projectKey: String
      projectName: String
      score: Float
    }

    type Project {
      id: ID!
      healthMetricsLatest: ProjectHealthMetric
      healthMetricsList(limit: Int): [ProjectHealthMetric!]!
    }

    input ProjectHealthMetricsFilter {
      """Dummy field to satisfy GraphQL spec for non-empty inputs"""
      dummy: Boolean
    }

    input OffsetPaginationInput {
      limit: Int
      offset: Int
    }

    enum ProjectHealthMetricsOrder {
      DUMMY
    }

    enum ExperienceLevelEnum {
      BEGINNER
      INTERMEDIATE
      ADVANCED
    }

    enum ProgramStatusEnum {
      DRAFT
      ACTIVE
      INACTIVE
    }

    input UpdateModuleInput {
      key: String
      name: String
      description: String
      experienceLevel: ExperienceLevelEnum
      startedAt: DateTime
      endedAt: DateTime
      tags: [String!]
      domains: [String!]
      projectId: String
    }

    input CreateModuleInput {
      key: String
      name: String
      description: String
      experienceLevel: ExperienceLevelEnum
      startedAt: DateTime
      endedAt: DateTime
      tags: [String!]
      domains: [String!]
      projectId: String
    }

    input UpdateProgramInput {
      key: String
      name: String
      description: String
      status: ProgramStatusEnum
      menteesLimit: Int
      startedAt: DateTime
      endedAt: DateTime
      tags: [String!]
      domains: [String!]
    }

    input CreateProgramInput {
      key: String
      name: String
      description: String
      menteesLimit: Int
      startedAt: DateTime
      endedAt: DateTime
      tags: [String!]
      domains: [String!]
    }

    input UpdateProgramStatusInput {
      key: String
      status: ProgramStatusEnum
    }
  `

  const documents = backendUp ? ['src/**/*.{ts,tsx}', '!src/types/__generated__/**'] : []

  return {
    documents,
    generates: {
      './src/': {
        config: {
          avoidOptionals: {
            // Use `null` for nullable fields instead of optionals
            field: true,
            // Allow nullable input fields to remain unspecified
            inputValue: false,
          },
          // Use `unknown` instead of `any` for unconfigured scalars
          defaultScalarType: 'unknown',
          scalars: {
            DateTime: 'string',
            UUID: 'string',
          },
          // Apollo Client always includes `__typename` fields
          nonOptionalTypename: true,
          // Apollo Client doesn't add the `__typename` field to root types so
          // don't generate a type for the `__typename` for root operation types.
          skipTypeNameForRoot: true,
        },
        // Order of plugins matter
        plugins: ['typescript-operations', 'typed-document-node'],
        preset: 'near-operation-file',
        presetConfig: {
          // This should be the file generated by the "typescript" plugin above,
          // relative to the directory specified for this configuration
          baseTypesPath: './types/__generated__/graphql.ts',
          // Relative to the source files
          folder: '../../types/__generated__',
        },
      },
      './src/types/__generated__/graphql.ts': {
        plugins: ['typescript'],
        config: {
          defaultScalarType: 'unknown',
          scalars: {
            DateTime: 'string',
            UUID: 'string',
          },
        },
      },
    },
    // Don't exit with non-zero status when there are no documents
    ignoreNoDocuments: true,
    overwrite: true,
    schema: backendUp
      ? csrfToken
        ? {
            [`${PUBLIC_API_URL}/graphql/`]: {
              headers: {
                Cookie: `csrftoken=${csrfToken}`,
                'X-CSRFToken': csrfToken,
              },
            },
          }
        : { [`${PUBLIC_API_URL}/graphql/`]: {} }
      : fallbackSchemaSDL,
  }
})()
