import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client'
import { Defer20220824Handler } from "@apollo/client/incremental";
import { LocalState } from "@apollo/client/local-state";
import { setContext } from '@apollo/client/link/context'
import { cookies } from 'next/headers'
import { fetchCsrfTokenServer } from 'server/fetchCsrfTokenServer'

async function createApolloClient() {
  const authLink = setContext(async (_, { headers }) => {
    let csrfToken = null
    const cookieValue = await getCsrfTokenOnServer()
    csrfToken = cookieValue
    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken ?? '',
        Cookie: csrfToken ? `csrftoken=${csrfToken}` : '',
      },
    }
  })
  const httpLink = new HttpLink({
    credentials: 'same-origin',
    uri: process.env.NEXT_SERVER_GRAPHQL_URL,
  })

  return new ApolloClient({
    cache: new InMemoryCache().restore(globalThis.__APOLLO_STATE__ ?? {}),
    link: authLink.concat(httpLink),
    ssrMode: true,

    /*
    Inserted by Apollo Client 3->4 migration codemod.
    If you are not using the `@client` directive in your application,
    you can safely remove this option.
    */
    localState: new LocalState({}),

    /*
    Inserted by Apollo Client 3->4 migration codemod.
    If you are not using the `@defer` directive in your application,
    you can safely remove this option.
    */
    incrementalHandler: new Defer20220824Handler()
  });
}

// This is a no-op Apollo client for end-to-end tests.
const noopApolloClient = {
  mutate: async () => ({ data: null }),
  query: async () => ({ data: null }),
}
export const apolloClient =
  process.env.NEXT_SERVER_DISABLE_SSR === 'true' ? noopApolloClient : await createApolloClient()

export const getCsrfTokenOnServer = async () => {
  const cookieStore = await cookies()
  const csrfCookie = cookieStore.get('csrftoken')

  return csrfCookie ? csrfCookie.value : await fetchCsrfTokenServer()
}

/*
Start: Inserted by Apollo Client 3->4 migration codemod.
Copy the contents of this block into a `.d.ts` file in your project to enable correct response types in your custom links.
If you do not use the `@defer` directive in your application, you can safely remove this block.
*/


import "@apollo/client";
import { Defer20220824Handler } from "@apollo/client/incremental";

declare module "@apollo/client" {
  export interface TypeOverrides extends Defer20220824Handler.TypeOverrides {}
}

/*
End: Inserted by Apollo Client 3->4 migration codemod.
*/

