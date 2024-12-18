import { Routes, Route } from 'react-router-dom'

import Footer from './components/Footer'
import Header from './components/Header'
import { Home, ProjectsComponent, CommitteesComponent, ChaptersComponent } from './pages'

function App() {
  return (
    <main className="m-0 flex min-h-screen w-full flex-col justify-start">
      <Header />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/projects" element={<ProjectsComponent />}></Route>
        <Route path="/committees" element={<CommitteesComponent />}></Route>
        <Route path="/chapters" element={<ChaptersComponent />}></Route>
      </Routes>
      <Footer />
    </main>
  )
}

export default App
