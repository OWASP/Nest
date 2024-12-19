import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { BrowserRouter } from 'react-router-dom'

import App from './App.tsx'
import ErrorWrapper from './ErrorWrapper'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ErrorWrapper>
        <App />
      </ErrorWrapper>
    </BrowserRouter>
  </StrictMode>
)
