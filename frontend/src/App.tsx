import { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'

import Footer from '@src/components/Footer'
import Header from '@src/components/Header'
import { Home, ProjectsPage, CommitteesPage, ChaptersPage } from '@src/pages'

function App() {
  const location = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location])

  return (
    <main className="flex min-h-screen w-full flex-col">
      <Header />
      <div className="mt-16 flex-1">
        <Routes>
          <Route path="/" element={<Home />}></Route>
          <Route path="/projects" element={<ProjectsPage />}></Route>
          <Route path="/committees" element={<CommitteesPage />}></Route>
          <Route path="/chapters" element={<ChaptersPage />}></Route>
        </Routes>
      </div>
      <Footer />
    </main>
  )
}

export default App
