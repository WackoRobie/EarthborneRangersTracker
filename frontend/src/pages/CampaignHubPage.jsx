import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Plus, Trash2, Minus } from 'lucide-react'
import { api } from '@/lib/api'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import PageHeader from '@/components/shared/PageHeader'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'
import MissionProgressBar from '@/components/shared/MissionProgressBar'

// ── Session Tab ──────────────────────────────────────────────────────────────

function SessionTab({ campaign, activeDay, missions, onMissionUpdate, onRefresh }) {
  const navigate = useNavigate()
  const [eventText, setEventText] = useState('')
  const [events, setEvents] = useState([])
  const [rewards, setRewards] = useState([])
  const [rewardCardName, setRewardCardName] = useState('')
  const [rewardQty, setRewardQty] = useState('1')
  const [newMissionName, setNewMissionName] = useState('')
  const [newMissionMax, setNewMissionMax] = useState('0')
  const [error, setError] = useState(null)

  const cid = campaign.id

  const loadEvents = useCallback(() => api.getEvents(cid).then(setEvents), [cid])
  const loadRewards = useCallback(() => api.getRewards(cid).then(setRewards), [cid])

  useEffect(() => {
    loadEvents()
    loadRewards()
  }, [loadEvents, loadRewards])

  const ongoingMissions = missions.filter((m) => !m.day_completed_id)

  async function addEvent() {
    if (!eventText.trim() || !activeDay) return
    try {
      await api.createEvent(cid, { day_id: activeDay.id, text: eventText.trim() })
      setEventText('')
      loadEvents()
    } catch (e) { setError(e.message) }
  }

  async function deleteEvent(eid) {
    try {
      await api.deleteEvent(cid, eid)
      loadEvents()
    } catch (e) { setError(e.message) }
  }

  async function adjustProgress(mission, delta) {
    const next = Math.max(0, Math.min(mission.max_progress || 3, mission.progress + delta))
    try {
      await api.patchMission(cid, mission.id, { progress: next })
      onMissionUpdate()
    } catch (e) { setError(e.message) }
  }

  async function completeMission(mission) {
    if (!activeDay) return
    try {
      await api.patchMission(cid, mission.id, { day_completed_id: activeDay.id })
      onMissionUpdate()
    } catch (e) { setError(e.message) }
  }

  async function addReward() {
    if (!rewardCardName.trim()) return
    try {
      await api.addReward(cid, { card_name: rewardCardName.trim(), quantity: parseInt(rewardQty) || 1 })
      setRewardCardName('')
      setRewardQty('1')
      loadRewards()
    } catch (e) { setError(e.message) }
  }

  async function addMission() {
    if (!newMissionName.trim()) return
    try {
      await api.createMission(cid, {
        name: newMissionName.trim(),
        max_progress: parseInt(newMissionMax) || 0,
      })
      setNewMissionName('')
      setNewMissionMax('0')
      onMissionUpdate()
    } catch (e) { setError(e.message) }
  }

  const todayEvents = activeDay
    ? events.filter((ev) => ev.day_id === activeDay.id)
    : []

  return (
    <div className="space-y-6">
      {error && <ErrorMessage message={error} />}

      {/* Session Start */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Session Start</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {activeDay ? (
            <>
              <div className="flex gap-2 items-center">
                <span className="text-muted-foreground w-28">Day</span>
                <span className="font-medium">Day {activeDay.day_number}</span>
              </div>
              <div className="flex gap-2 items-center">
                <span className="text-muted-foreground w-28">Weather</span>
                <Badge variant="outline">{activeDay.weather}</Badge>
              </div>
              {activeDay.location && (
                <div className="flex gap-2 items-center">
                  <span className="text-muted-foreground w-28">Location</span>
                  <span>{activeDay.location}</span>
                </div>
              )}
              {activeDay.path_terrain && (
                <div className="flex gap-2 items-center">
                  <span className="text-muted-foreground w-28">Path Terrain</span>
                  <span>{activeDay.path_terrain}</span>
                </div>
              )}
            </>
          ) : (
            <p className="text-muted-foreground">No active day.</p>
          )}
          {ongoingMissions.length > 0 && (
            <>
              <Separator className="my-2" />
              <p className="text-muted-foreground font-medium">Ongoing Missions</p>
              {ongoingMissions.map((m) => (
                <div key={m.id}>
                  <p className="font-medium">{m.name}</p>
                  <MissionProgressBar mission={m} />
                </div>
              ))}
            </>
          )}
        </CardContent>
      </Card>

      {/* Notable Events */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Notable Events</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {todayEvents.length === 0 && (
            <p className="text-sm text-muted-foreground">No events recorded today.</p>
          )}
          {todayEvents.map((ev) => (
            <div key={ev.id} className="flex items-start gap-2">
              <p className="text-sm flex-1">{ev.text}</p>
              <Button variant="ghost" size="icon" className="h-6 w-6 shrink-0" onClick={() => deleteEvent(ev.id)}>
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
          <div className="flex gap-2 pt-1">
            <Textarea
              placeholder="Record a notable event..."
              value={eventText}
              onChange={(e) => setEventText(e.target.value)}
              className="min-h-[60px]"
            />
            <Button onClick={addEvent} disabled={!eventText.trim() || !activeDay} className="shrink-0">
              Add
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Mission Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Mission Progress</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {ongoingMissions.length === 0 && (
            <p className="text-sm text-muted-foreground">No ongoing missions.</p>
          )}
          {ongoingMissions.map((m) => (
            <div key={m.id} className="space-y-1">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">{m.name}</p>
                <div className="flex items-center gap-1">
                  {m.max_progress > 0 && (
                    <>
                      <Button variant="ghost" size="icon" className="h-6 w-6"
                        onClick={() => adjustProgress(m, -1)} disabled={m.progress <= 0}>
                        <Minus className="h-3 w-3" />
                      </Button>
                      <span className="text-sm w-8 text-center">{m.progress}/{m.max_progress}</span>
                      <Button variant="ghost" size="icon" className="h-6 w-6"
                        onClick={() => adjustProgress(m, 1)} disabled={m.progress >= m.max_progress}>
                        <Plus className="h-3 w-3" />
                      </Button>
                    </>
                  )}
                  <Button variant="outline" size="sm" className="ml-2 h-6 text-xs"
                    onClick={() => completeMission(m)} disabled={!activeDay}>
                    Complete
                  </Button>
                </div>
              </div>
              <MissionProgressBar mission={m} />
            </div>
          ))}

          <Separator />
          <p className="text-sm font-medium">Add Mission</p>
          <div className="flex gap-2">
            <Input
              placeholder="Mission name"
              value={newMissionName}
              onChange={(e) => setNewMissionName(e.target.value)}
            />
            <Select value={newMissionMax} onValueChange={setNewMissionMax}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Max" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">Pass/fail</SelectItem>
                <SelectItem value="1">Max 1</SelectItem>
                <SelectItem value="2">Max 2</SelectItem>
                <SelectItem value="3">Max 3</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={addMission} disabled={!newMissionName.trim()}>Add</Button>
          </div>
        </CardContent>
      </Card>

      {/* Add Reward */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add Reward to Pool</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Input
              placeholder="Card name..."
              value={rewardCardName}
              onChange={(e) => setRewardCardName(e.target.value)}
              className="flex-1"
            />
            <Input
              type="number"
              min="1"
              max="10"
              value={rewardQty}
              onChange={(e) => setRewardQty(e.target.value)}
              className="w-20"
            />
            <Button onClick={addReward} disabled={!rewardCardName.trim()}>Add</Button>
          </div>
        </CardContent>
      </Card>

      {/* Close Day */}
      <div className="flex justify-end">
        <Button
          size="lg"
          onClick={() => navigate(`/campaigns/${cid}/session/close`)}
          disabled={!activeDay}
        >
          Close Day →
        </Button>
      </div>
    </div>
  )
}

// ── Missions Tab ─────────────────────────────────────────────────────────────

function MissionsTab({ campaign, missions, onRefresh }) {
  const [newMissionName, setNewMissionName] = useState('')
  const [newMissionMax, setNewMissionMax] = useState('0')
  const [error, setError] = useState(null)

  async function addMission() {
    if (!newMissionName.trim()) return
    try {
      await api.createMission(campaign.id, {
        name: newMissionName.trim(),
        max_progress: parseInt(newMissionMax) || 0,
      })
      setNewMissionName('')
      setNewMissionMax('0')
      onRefresh()
    } catch (e) { setError(e.message) }
  }

  return (
    <div className="space-y-4">
      {error && <ErrorMessage message={error} />}

      <Card>
        <CardContent className="pt-4 space-y-2">
          <div className="flex gap-2">
            <Input
              placeholder="Mission name"
              value={newMissionName}
              onChange={(e) => setNewMissionName(e.target.value)}
            />
            <Select value={newMissionMax} onValueChange={setNewMissionMax}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Max" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">Pass/fail</SelectItem>
                <SelectItem value="1">Max 1</SelectItem>
                <SelectItem value="2">Max 2</SelectItem>
                <SelectItem value="3">Max 3</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={addMission} disabled={!newMissionName.trim()}>
              <Plus className="h-4 w-4 mr-1" />
              Add
            </Button>
          </div>
        </CardContent>
      </Card>

      {missions.length === 0 && (
        <p className="text-center text-muted-foreground py-8">No missions yet.</p>
      )}

      {missions.map((m) => (
        <Card key={m.id}>
          <CardContent className="pt-4 space-y-2">
            <div className="flex items-start justify-between">
              <p className="font-medium">{m.name}</p>
              {m.day_completed_id ? (
                <Badge variant="secondary">Completed</Badge>
              ) : (
                <Badge variant="outline">Ongoing</Badge>
              )}
            </div>
            <MissionProgressBar mission={m} />
            <p className="text-xs text-muted-foreground">
              Started day {m.day_started_id ?? '—'}
              {m.day_completed_id && ` · Completed day ${m.day_completed_id}`}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// ── Rangers Tab ───────────────────────────────────────────────────────────────

function RangersTab({ campaign, rangers }) {
  const navigate = useNavigate()
  const cid = campaign.id

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={() => navigate(`/campaigns/${cid}/rangers/new`)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Ranger
        </Button>
      </div>

      {rangers.length === 0 && (
        <p className="text-center text-muted-foreground py-8">No rangers yet.</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {rangers.map((r) => (
          <Card
            key={r.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate(`/campaigns/${cid}/rangers/${r.id}`)}
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">{r.name}</CardTitle>
              <p className="text-sm text-muted-foreground">{r.aspect_card_name}</p>
            </CardHeader>
            <CardContent>
              <div className="flex gap-3 text-sm">
                <span><span className="text-muted-foreground">AWA</span> {r.awa}</span>
                <span><span className="text-muted-foreground">FIT</span> {r.fit}</span>
                <span><span className="text-muted-foreground">FOC</span> {r.foc}</span>
                <span><span className="text-muted-foreground">SPI</span> {r.spi}</span>
              </div>
              {r.current_decklist?.length > 0 && (
                <p className="text-xs text-muted-foreground mt-1">
                  {r.current_decklist.reduce((s, e) => s + e.quantity, 0)} cards in deck
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// ── Rewards Tab ───────────────────────────────────────────────────────────────

function RewardsTab({ campaign }) {
  const [rewards, setRewards] = useState([])
  const [rewardCardName, setRewardCardName] = useState('')
  const [rewardQty, setRewardQty] = useState('1')
  const [error, setError] = useState(null)

  const cid = campaign.id

  const loadRewards = useCallback(() => api.getRewards(cid).then(setRewards), [cid])

  useEffect(() => {
    loadRewards()
  }, [loadRewards])

  async function addReward() {
    if (!rewardCardName.trim()) return
    try {
      await api.addReward(cid, { card_name: rewardCardName.trim(), quantity: parseInt(rewardQty) || 1 })
      setRewardCardName('')
      setRewardQty('1')
      loadRewards()
    } catch (e) { setError(e.message) }
  }

  async function removeReward(rwid) {
    try {
      await api.removeReward(cid, rwid)
      loadRewards()
    } catch (e) { setError(e.message) }
  }

  return (
    <div className="space-y-4">
      {error && <ErrorMessage message={error} />}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add to Pool</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Card name..."
              value={rewardCardName}
              onChange={(e) => setRewardCardName(e.target.value)}
              className="flex-1"
            />
            <Input
              type="number"
              min="1"
              max="10"
              value={rewardQty}
              onChange={(e) => setRewardQty(e.target.value)}
              className="w-20"
            />
            <Button onClick={addReward} disabled={!rewardCardName.trim()}>Add</Button>
          </div>
        </CardContent>
      </Card>

      {rewards.length === 0 && (
        <p className="text-center text-muted-foreground py-8">Rewards pool is empty.</p>
      )}

      {rewards.length > 0 && (
        <Card>
          <CardContent className="pt-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-muted-foreground text-left">
                  <th className="pb-2">Card</th>
                  <th className="pb-2 text-right">Qty</th>
                  <th className="pb-2"></th>
                </tr>
              </thead>
              <tbody>
                {rewards.map((rw) => (
                  <tr key={rw.id} className="border-t">
                    <td className="py-2">{rw.card_name}</td>
                    <td className="py-2 text-right">{rw.quantity}</td>
                    <td className="py-2 text-right">
                      <Button variant="ghost" size="icon" className="h-6 w-6"
                        onClick={() => removeReward(rw.id)}>
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function CampaignHubPage() {
  const { id } = useParams()
  const [campaign, setCampaign] = useState(null)
  const [missions, setMissions] = useState([])
  const [rangers, setRangers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadMissions = useCallback(() => api.getMissions(id).then(setMissions), [id])
  const loadRangers = useCallback(() => api.getRangers(id).then(setRangers), [id])

  useEffect(() => {
    Promise.all([api.getCampaign(id), loadMissions(), loadRangers()])
      .then(([c]) => setCampaign(c))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id, loadMissions, loadRangers])

  if (loading) return <div className="container max-w-4xl mx-auto p-6"><LoadingSpinner /></div>
  if (error) return <div className="container max-w-4xl mx-auto p-6"><ErrorMessage message={error} /></div>
  if (!campaign) return null

  const activeDay = campaign.days?.find((d) => d.status === 'active') ?? null

  return (
    <div className="container max-w-4xl mx-auto p-6">
      <div className="flex items-start justify-between mb-2">
        <PageHeader title={campaign.name} backTo="/" />
        <Badge variant={campaign.status === 'active' ? 'default' : 'secondary'} className="mt-1">
          {campaign.status}
        </Badge>
      </div>
      <p className="text-sm text-muted-foreground mb-6">{campaign.storyline?.name}</p>

      <Tabs defaultValue="session">
        <TabsList className="mb-4">
          <TabsTrigger value="session">Session</TabsTrigger>
          <TabsTrigger value="missions">Missions</TabsTrigger>
          <TabsTrigger value="rangers">Rangers</TabsTrigger>
          <TabsTrigger value="rewards">Rewards</TabsTrigger>
        </TabsList>

        <TabsContent value="session">
          <SessionTab
            campaign={campaign}
            activeDay={activeDay}
            missions={missions}
            onMissionUpdate={loadMissions}
            onRefresh={() => {}}
          />
        </TabsContent>

        <TabsContent value="missions">
          <MissionsTab campaign={campaign} missions={missions} onRefresh={loadMissions} />
        </TabsContent>

        <TabsContent value="rangers">
          <RangersTab campaign={campaign} rangers={rangers} />
        </TabsContent>

        <TabsContent value="rewards">
          <RewardsTab campaign={campaign} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
