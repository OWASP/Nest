
import { ApolloProvider } from '@apollo/client'
import { ChakraProvider, defaultSystem } from '@chakra-ui/react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import TagManager from 'react-gtm-module'
import { BrowserRouter } from 'react-router-dom'

import { GTM_AUTH, GTM_ID, GTM_PREVIEW } from 'utils/credentials.ts'
import apolloClient from 'utils/helpers/apolloClient.ts'
import { ErrorWrapper } from 'wrappers/ErrorWrapper.tsx'
import App from './App.tsx'

const tagManagerArgs = {
  gtmId: GTM_ID,
  auth: GTM_AUTH,
  preview: GTM_PREVIEW,
}

TagManager.initialize(tagManagerArgs)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ErrorWrapper>
        <ApolloProvider client={apolloClient}>
         <ChakraProvider value={defaultSystem}>
           <App />
          </ChakraProvider>
        </ApolloProvider>
      </ErrorWrapper>
    </BrowserRouter>
  </StrictMode>
)
