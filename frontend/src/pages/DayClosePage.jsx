import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import PageHeader from '@/components/shared/PageHeader'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'

const PATH_TERRAINS = ['Forest', 'Grassland', 'Marsh', 'Mountain', 'River', 'Scrubland']

function RangerTradePanel({ ranger, rewards }) {
  const cid = ranger.campaign_id
  const [decklist, setDecklist] = useState([])

  const loadRanger = useCallback(async () => {
    const r = await api.getRanger(cid, ranger.id)
    setDecklist(r.current_decklist ?? [])
  }, [cid, ranger.id])

  useEffect(() => { loadRanger() }, [loadRanger])

  const activeRewards = rewards.filter((rw) => rw.quantity > 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{ranger.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-medium text-muted-foreground mb-2">Current Deck</p>
            {decklist.length === 0
              ? <p className="text-muted-foreground italic">Empty</p>
              : decklist.map((e) => (
                <div key={e.card.id} className="flex justify-between py-0.5">
                  <span>{e.card.name}</span>
                  <span className="text-muted-foreground">×{e.quantity}</span>
                </div>
              ))
            }
          </div>
          <div>
            <p className="font-medium text-muted-foreground mb-2">Rewards Pool</p>
            {activeRewards.length === 0
              ? <p className="text-muted-foreground italic">Empty</p>
              : activeRewards.map((rw) => (
                <div key={rw.id} className="flex justify-between py-0.5">
                  <span>{rw.card_name}</span>
                  <span className="text-muted-foreground">×{rw.quantity}</span>
                </div>
              ))
            }
          </div>
        </div>
        <p className="text-xs text-muted-foreground border-t pt-3">
          Trade recording will be available once the card library is linked to the rewards pool.
          Record any trades made on your physical cards — deck rebuilding reference above.
        </p>
      </CardContent>
    </Card>
  )
}

export default function DayClosePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [campaign, setCampaign] = useState(null)
  const [rangers, setRangers] = useState([])
  const [rewards, setRewards] = useState([])
  const [location, setLocation] = useState('')
  const [pathTerrain, setPathTerrain] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const loadRewards = useCallback(() => api.getRewards(id).then(setRewards), [id])

  useEffect(() => {
    Promise.all([api.getCampaign(id), api.getRangers(id), loadRewards()])
      .then(([c, r]) => { setCampaign(c); setRangers(r) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id, loadRewards])

  if (loading) return <div className="container max-w-2xl mx-auto p-6"><LoadingSpinner /></div>
  if (error) return <div className="container max-w-2xl mx-auto p-6"><ErrorMessage message={error} /></div>
  if (!campaign) return null

  const activeDay = campaign.days?.find((d) => d.status === 'active') ?? null

  async function handleClose() {
    if (!location.trim() || !pathTerrain || !activeDay) return
    setSubmitting(true)
    setError(null)
    try {
      await api.closeDay(id, activeDay.id, {
        location: location.trim(),
        path_terrain: pathTerrain,
      })
      navigate(`/campaigns/${id}`)
    } catch (e) {
      setError(e.message)
      setSubmitting(false)
    }
  }

  return (
    <div className="container max-w-2xl mx-auto p-6">
      <PageHeader title="Close Day" backTo={`/campaigns/${id}`} />

      {error && <ErrorMessage message={error} />}

      {!activeDay && (
        <ErrorMessage message="No active day found. Cannot close." />
      )}

      {activeDay && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Next Session Setup</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Record where the rangers are headed (this will appear at the start of the next session).
              </p>
              <div className="space-y-2">
                <Label htmlFor="location">Destination Location</Label>
                <Input
                  id="location"
                  placeholder="Where are the rangers going?"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="path">Path Terrain</Label>
                <Select value={pathTerrain} onValueChange={setPathTerrain}>
                  <SelectTrigger id="path">
                    <SelectValue placeholder="Select terrain..." />
                  </SelectTrigger>
                  <SelectContent>
                    {PATH_TERRAINS.map((t) => (
                      <SelectItem key={t} value={t}>{t}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {rangers.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">Deck Trades</h2>
              {rangers.map((r) => (
                <RangerTradePanel
                  key={r.id}
                  ranger={r}
                  rewards={rewards}
                />
              ))}
            </div>
          )}

          <div className="flex justify-end">
            <Button
              size="lg"
              onClick={handleClose}
              disabled={submitting || !location.trim() || !pathTerrain}
            >
              {submitting ? 'Closing...' : 'Close Day & Advance'}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
