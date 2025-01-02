import { Home, ProjectsPage, CommitteesPage, ChaptersPage, ContributePage } from 'pages'
import { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'

import { ErrorDisplay, ERROR_CONFIGS } from 'lib/ErrorHandler'
import Footer from 'components/Footer'
import Header from 'components/Header'
import { Toaster } from 'components/ui/toaster'

function App() {
  const location = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location])

  return (
    <main className="flex min-h-screen w-full flex-col">
      <Toaster />
      <Header />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/projects" element={<ProjectsPage />}></Route>
        <Route path="/projects/contribute" element={<ContributePage />}></Route>
        <Route path="/committees" element={<CommitteesPage />}></Route>
        <Route path="/chapters" element={<ChaptersPage />}></Route>
        <Route path="*" element={<ErrorDisplay {...ERROR_CONFIGS['404']} />} />
      </Routes>
      <Footer />
    </main>
  )
}

export default App
