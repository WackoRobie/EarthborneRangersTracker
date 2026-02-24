import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'

export default function CampaignListPage() {
  const navigate = useNavigate()
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getCampaigns()
      .then(setCampaigns)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="container max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Earthborne Rangers</h1>
        <Button onClick={() => navigate('/campaigns/new')}>
          <Plus className="h-4 w-4 mr-2" />
          New Campaign
        </Button>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && campaigns.length === 0 && (
        <div className="text-center py-16 text-muted-foreground">
          <p className="text-lg">No campaigns yet.</p>
          <p className="text-sm mt-1">Create your first campaign to get started.</p>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {campaigns.map((c) => (
          <Card
            key={c.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate(`/campaigns/${c.id}`)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg">{c.name}</CardTitle>
                <Badge variant={c.status === 'active' ? 'default' : 'secondary'}>
                  {c.status}
                </Badge>
              </div>
              <CardDescription>{c.storyline?.name}</CardDescription>
            </CardHeader>
            <CardContent>
              {c.current_day && (
                <p className="text-sm text-muted-foreground">
                  Day {c.current_day.day_number} — {c.current_day.weather}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
