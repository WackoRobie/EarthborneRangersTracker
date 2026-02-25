import { Navigate, Routes, Route, useLocation } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Toaster } from '@/components/ui/toaster'
import CampaignListPage from '@/pages/CampaignListPage'
import CampaignCreatePage from '@/pages/CampaignCreatePage'
import CampaignHubPage from '@/pages/CampaignHubPage'
import DayClosePage from '@/pages/DayClosePage'
import RangerCreatePage from '@/pages/RangerCreatePage'
import RangerDetailPage from '@/pages/RangerDetailPage'
import LoginPage from '@/pages/LoginPage'

function RequireAuth({ children }) {
  const location = useLocation()
  if (!isAuthenticated()) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />
  }
  return children
}

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<RequireAuth><CampaignListPage /></RequireAuth>} />
        <Route path="/campaigns/new" element={<RequireAuth><CampaignCreatePage /></RequireAuth>} />
        <Route path="/campaigns/:id" element={<RequireAuth><CampaignHubPage /></RequireAuth>} />
        <Route path="/campaigns/:id/session/close" element={<RequireAuth><DayClosePage /></RequireAuth>} />
        <Route path="/campaigns/:id/rangers/new" element={<RequireAuth><RangerCreatePage /></RequireAuth>} />
        <Route path="/campaigns/:id/rangers/:rangerId" element={<RequireAuth><RangerDetailPage /></RequireAuth>} />
      </Routes>
      <Toaster />
    </>
  )
}
