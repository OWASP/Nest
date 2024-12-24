import { render } from '@testing-library/react'
import { ReactNode } from 'react'
import { BrowserRouter } from 'react-router-dom'

const customRender = (ui: ReactNode) => {
  return render(<BrowserRouter>{ui}</BrowserRouter>)
}

export * from '@testing-library/react'
export { customRender as render }
