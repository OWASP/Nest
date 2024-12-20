import { Routes, Route } from 'react-router-dom'

import ErrorMessage from './components/ErrorMessage'
import Footer from './components/Footer'
import Header from './components/Header'
import { Home, ProjectsPage, CommitteesPage, ChaptersPage } from './pages'

function App() {
  return (
    <main className="m-0 flex min-h-screen w-full flex-col justify-start">
      <Header />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/projects" element={<ProjectsPage />}></Route>
        <Route path="/committees" element={<CommitteesPage />}></Route>
        <Route path="/chapters" element={<ChaptersPage />}></Route>
        <Route path="*" element={<ErrorMessage message="Page not found." statusCode={404} />} />
      </Routes>
      <Footer />
    </main>
  )
}

export default App
