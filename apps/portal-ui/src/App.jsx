import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import CouncilPage from './pages/CouncilPage'
import JobbernautPage from './pages/JobbernautPage'
import MatcherPage from './pages/MatcherPage'
import AutoJobApply from './pages/AutoJobApply'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="council" element={<CouncilPage />} />
        <Route path="jobbernaut" element={<JobbernautPage />} />
        <Route path="matcher" element={<MatcherPage />} />
        <Route path="auto-apply" element={<AutoJobApply />} />
        {/* Future routes */}
        <Route path="resume-lm" element={<ComingSoon name="ResumeLM" />} />
        <Route path="aihawk" element={<ComingSoon name="AIHawk" />} />
      </Route>
    </Routes>
  )
}

function ComingSoon({ name }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="text-6xl mb-6">🚧</div>
      <h1 className="font-display text-3xl font-bold mb-4">{name}</h1>
      <p className="text-sand-400">Coming soon...</p>
    </div>
  )
}

export default App

