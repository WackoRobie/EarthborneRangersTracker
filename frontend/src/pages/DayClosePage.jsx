import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { RotateCcw } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import PageHeader from '@/components/shared/PageHeader'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'

const PATH_TERRAINS = ['Forest', 'Grassland', 'Marsh', 'Mountain', 'River', 'Scrubland']

function RangerTradePanel({ ranger, activeDay, rewards, onTradeComplete }) {
  const cid = ranger.campaign_id
  const [origCardId, setOrigCardId] = useState('')
  const [rewardCardId, setRewardCardId] = useState('')
  const [trades, setTrades] = useState([])
  const [decklist, setDecklist] = useState([])
  const [error, setError] = useState(null)

  const loadRanger = useCallback(async () => {
    const r = await api.getRanger(cid, ranger.id)
    setDecklist(r.current_decklist ?? [])
    setTrades(r.trades ?? [])
  }, [cid, ranger.id])

  useEffect(() => { loadRanger() }, [loadRanger])

  const activeRewards = rewards.filter((rw) => rw.quantity > 0)

  async function executeTrade() {
    if (!origCardId || !rewardCardId || !activeDay) return
    try {
      await api.createTrade(cid, ranger.id, {
        day_id: activeDay.id,
        original_card_id: parseInt(origCardId),
        reward_card_id: parseInt(rewardCardId),
      })
      setOrigCardId('')
      setRewardCardId('')
      await loadRanger()
      onTradeComplete()
    } catch (e) { setError(e.message) }
  }

  async function revertTrade(tid) {
    try {
      await api.revertTrade(cid, ranger.id, tid)
      await loadRanger()
      onTradeComplete()
    } catch (e) { setError(e.message) }
  }

  const nonReverted = trades.filter((t) => !t.reverted)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{ranger.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && <ErrorMessage message={error} />}

        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <Label className="text-xs">Trade away (from deck)</Label>
            <Select value={origCardId} onValueChange={setOrigCardId}>
              <SelectTrigger>
                <SelectValue placeholder="Select card..." />
              </SelectTrigger>
              <SelectContent>
                {decklist.map((entry) => (
                  <SelectItem key={entry.card.id} value={String(entry.card.id)}>
                    {entry.card.name} ×{entry.quantity}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Receive (from pool)</Label>
            <Select value={rewardCardId} onValueChange={setRewardCardId}>
              <SelectTrigger>
                <SelectValue placeholder="Select card..." />
              </SelectTrigger>
              <SelectContent>
                {activeRewards.map((rw) => (
                  <SelectItem key={rw.id} value={String(rw.card_id)}>
                    {rw.card?.name ?? rw.card_id} ×{rw.quantity}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <Button onClick={executeTrade} disabled={!origCardId || !rewardCardId || !activeDay} size="sm">
          Execute Trade
        </Button>

        {nonReverted.length > 0 && (
          <>
            <Separator />
            <p className="text-sm font-medium">Recorded Trades</p>
            {nonReverted.map((t) => (
              <div key={t.id} className="flex items-center justify-between text-sm">
                <span>
                  <span className="text-muted-foreground">{t.original_card?.name}</span>
                  {' → '}
                  <span className="font-medium">{t.reward_card?.name}</span>
                </span>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => revertTrade(t.id)}>
                  <RotateCcw className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </>
        )}
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
                  activeDay={activeDay}
                  rewards={rewards}
                  onTradeComplete={loadRewards}
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
