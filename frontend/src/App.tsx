import { Routes, Route } from 'react-router-dom'

import Footer from './components/Footer'
import Header from './components/Header'
import { Home, ProjectsPage, CommitteesPage, ChaptersPage, ContributePage } from './pages'

function App() {
  return (
    <main className="m-0 flex min-h-screen w-full flex-col justify-start">
      <Header />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/projects" element={<ProjectsPage />}></Route>
        <Route path="/projects/contribute" element={<ContributePage />}></Route>
        <Route path="/committees" element={<CommitteesPage />}></Route>
        <Route path="/chapters" element={<ChaptersPage />}></Route>
      </Routes>
      <Footer />
    </main>
  )
}

export default App
