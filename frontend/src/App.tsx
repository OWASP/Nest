import { Home, ProjectsPage, CommitteesPage, ChaptersPage, ContributePage } from 'pages'
import { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'

import Footer from 'components/Footer'
import Header from 'components/Header'
import { NotFoundPage } from './components/NotFoundPage'

function App() {
  const location = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location])

  return (
    <main className="flex min-h-screen w-full flex-col">
      <Header />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/projects" element={<ProjectsPage />}></Route>
        <Route path="/projects/contribute" element={<ContributePage />}></Route>
        <Route path="/committees" element={<CommitteesPage />}></Route>
        <Route path="/chapters" element={<ChaptersPage />}></Route>
        <Route path="*" element={<NotFoundPage />}></Route>
      </Routes>
      <Footer />
    </main>
  )
}

export default App
