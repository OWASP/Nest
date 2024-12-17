import { Routes, Route } from 'react-router-dom'

import Footer from './components/Footer'
import Header from './components/Header'
import { Chapters, Committees, Home, Projects } from './pages'

function App() {
  return (
    <main className="m-0 flex min-h-screen w-full flex-col justify-start">
      <Header />
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/projects" element={<Projects />}></Route>
        <Route path="/committees" element={<Committees />}></Route>
        <Route path="/chapters" element={<Chapters />}></Route>
      </Routes>
      <Footer />
    </main>
  )
}

export default App
