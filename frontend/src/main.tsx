import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter } from 'react-router-dom'

import App from './App.tsx'
import ErrorWrapper from './ErrorWrapper'
import TagManager from 'react-gtm-module'
import { GTM_AUTH, GTM_ID, GTM_PREVIEW } from 'utils/credentials.ts'

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
        <App />
      </ErrorWrapper>
    </BrowserRouter>
  </StrictMode>
)
