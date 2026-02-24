import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import PageHeader from '@/components/shared/PageHeader'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'

export default function CampaignCreatePage() {
  const navigate = useNavigate()
  const [storylines, setStorylines] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [name, setName] = useState('')
  const [storylineId, setStorylineId] = useState('')

  useEffect(() => {
    api.getStorylines()
      .then(setStorylines)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim() || !storylineId) return
    setSubmitting(true)
    setError(null)
    try {
      const campaign = await api.createCampaign({ name: name.trim(), storyline_id: parseInt(storylineId) })
      navigate(`/campaigns/${campaign.id}`)
    } catch (e) {
      setError(e.message)
      setSubmitting(false)
    }
  }

  return (
    <div className="container max-w-lg mx-auto p-6">
      <PageHeader title="New Campaign" backTo="/" />

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {!loading && (
        <Card>
          <CardHeader>
            <CardTitle>Campaign Details</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Campaign Name</Label>
                <Input
                  id="name"
                  placeholder="Enter campaign name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="storyline">Storyline</Label>
                <Select value={storylineId} onValueChange={setStorylineId}>
                  <SelectTrigger id="storyline">
                    <SelectValue placeholder="Select a storyline" />
                  </SelectTrigger>
                  <SelectContent>
                    {storylines.map((s) => (
                      <SelectItem key={s.id} value={String(s.id)}>
                        {s.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button type="submit" className="w-full" disabled={submitting || !name.trim() || !storylineId}>
                {submitting ? 'Creating...' : 'Create Campaign'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
