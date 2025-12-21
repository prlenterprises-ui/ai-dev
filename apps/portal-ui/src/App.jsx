import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import CouncilPage from './pages/CouncilPage'
import AutoJobApply from './pages/AutoJobApply'
import AdminPage from './pages/AdminPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="council" element={<CouncilPage />} />
        <Route path="auto-apply" element={<AutoJobApply />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>
    </Routes>
  )
}

export default App

