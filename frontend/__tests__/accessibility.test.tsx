import { render, waitFor } from '@testing-library/react'
import App from 'App'
import { axe, toHaveNoViolations } from 'jest-axe'
import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { ChaptersPage } from 'pages/index'

expect.extend(toHaveNoViolations)

const renderWithRouter = (Component: React.ComponentType) => {
  return render(
    <BrowserRouter>
      <Component />
    </BrowserRouter>
  )
}

describe('Accessibility Tests', () => {
  jest.setTimeout(30000)

  it('App should have no accessibility violations', async () => {
    const { container } = renderWithRouter(App)

    await waitFor(() => container)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  const pages = [{ component: ChaptersPage, name: 'ChapterPage' }]

  describe.each(pages)('Testing individual pages', ({ component: PageComponent, name }) => {
    it(`${name} should have no accessibility violations`, async () => {
      const { container } = renderWithRouter(PageComponent)

      await waitFor(() => container)

      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })
  })
})
