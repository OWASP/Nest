import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client'
import { Defer20220824Handler } from "@apollo/client/incremental";
import { LocalState } from "@apollo/client/local-state";
import { setContext } from '@apollo/client/link/context'
import { AppError, handleAppError } from 'app/global-error'
import { GRAPHQL_URL } from 'utils/credentials'
import { getCsrfToken } from 'utils/utility'
const createApolloClient = () => {
  if (!GRAPHQL_URL) {
    const error = new AppError(500, 'Missing GraphQL URL')
    handleAppError(error)
    return null
  }

  const httpLink = new HttpLink({
    credentials: 'include',
    uri: GRAPHQL_URL,
  })

  const authLink = setContext(async (_, { headers }) => {
    const csrfToken = await getCsrfToken()

    return {
      headers: {
        ...headers,
        'X-CSRFToken': csrfToken || '',
      },
    }
  })

  return new ApolloClient({
    cache: new InMemoryCache(),
    link: authLink.concat(httpLink),

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
const apolloClient = createApolloClient()

export default apolloClient

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

