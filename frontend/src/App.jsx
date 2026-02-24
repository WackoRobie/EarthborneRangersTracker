import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import CampaignListPage from '@/pages/CampaignListPage'
import CampaignCreatePage from '@/pages/CampaignCreatePage'
import CampaignHubPage from '@/pages/CampaignHubPage'
import DayClosePage from '@/pages/DayClosePage'
import RangerCreatePage from '@/pages/RangerCreatePage'
import RangerDetailPage from '@/pages/RangerDetailPage'

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<CampaignListPage />} />
        <Route path="/campaigns/new" element={<CampaignCreatePage />} />
        <Route path="/campaigns/:id" element={<CampaignHubPage />} />
        <Route path="/campaigns/:id/session/close" element={<DayClosePage />} />
        <Route path="/campaigns/:id/rangers/new" element={<RangerCreatePage />} />
        <Route path="/campaigns/:id/rangers/:rangerId" element={<RangerDetailPage />} />
      </Routes>
      <Toaster />
    </>
  )
}
