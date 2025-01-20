import axe from '@axe-core/react'
import React, { StrictMode } from 'react'
import ReactDOM from 'react-dom'
import { createRoot } from 'react-dom/client'
import './index.css'
import TagManager from 'react-gtm-module'
import { BrowserRouter } from 'react-router-dom'

import { GTM_AUTH, GTM_ID, GTM_PREVIEW } from 'utils/credentials.ts'
import { ErrorWrapper } from 'wrappers/ErrorWrapper.tsx'
import App from './App.tsx'

const tagManagerArgs = {
  gtmId: GTM_ID,
  auth: GTM_AUTH,
  preview: GTM_PREVIEW,
}

TagManager.initialize(tagManagerArgs)

if (process.env.NODE_ENV !== 'development') {
  axe(React, ReactDOM, 1000)
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ErrorWrapper>
        <App />
      </ErrorWrapper>
    </BrowserRouter>
  </StrictMode>
)
