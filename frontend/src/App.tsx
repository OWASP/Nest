import {
  Home,
  ProjectsPage,
  CommitteesPage,
  ChaptersPage,
  ContributePage,
  ProjectDetailsPage,
  CommitteeDetailsPage,
  ChapterDetailsPage,
  UsersPage,
  UserDetailsPage
} from 'pages'
import { useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'

import Footer from 'components/Footer'
import Header from 'components/Header'

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
        <Route path="/projects/:projectKey" element={<ProjectDetailsPage />}></Route>
        <Route path="/projects/contribute" element={<ContributePage />}></Route>
        <Route path="/committees" element={<CommitteesPage />}></Route>
        <Route path="/committees/:committeeKey" element={<CommitteeDetailsPage />}></Route>
        <Route path="/chapters" element={<ChaptersPage />}></Route>
        <Route path="/chapters/:chapterKey" element={<ChapterDetailsPage />}></Route>
        <Route path="/community/users" element={<UsersPage />}></Route>
        <Route path="/community/users/:userKey" element={<UserDetailsPage />}></Route>
      </Routes>
      <Footer />
    </main>
  )
}

export default App
