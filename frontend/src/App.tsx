import {
  ChapterDetailsPage,
  ChaptersPage,
  CommitteeDetailsPage,
  CommitteesPage,
  ContributePage,
  Home,
  ProjectDetailsPage,
  ProjectsPage,
  RepositoryDetailsPage,
  UserDetailsPage,
  RepositoryDetailsPage,
} from 'pages'
import { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import { ERROR_CONFIGS, ErrorDisplay } from 'wrappers/ErrorWrapper'

import Footer from 'components/Footer'
import Header from 'components/Header'
import { Toaster } from 'components/ui/Toaster'
import ScrollUp from './components/ScrollUp'
import './components/ScrollUp.css'

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
        <Route path="/projects/:projectKey" element={<ProjectDetailsPage />}></Route>
        <Route
          path="/projects/:projectKey/repositories/:repositoryKey"
          element={<RepositoryDetailsPage />}
        ></Route>
        <Route path="/projects/contribute" element={<ContributePage />}></Route>
        <Route path="/committees" element={<CommitteesPage />}></Route>
        <Route path="/committees/:committeeKey" element={<CommitteeDetailsPage />}></Route>
        <Route path="/chapters" element={<ChaptersPage />}></Route>
        <Route path="/chapters/:chapterKey" element={<ChapterDetailsPage />}></Route>
        <Route path="/community/users" element={<UsersPage />}></Route>
        <Route path="/community/users/:userKey" element={<UserDetailsPage />}></Route>
        <Route path="*" element={<ErrorDisplay {...ERROR_CONFIGS['404']} />} />
      </Routes>
      <Footer />
      <ScrollUp />
    </main>
  )
}

export default App
