import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Archive, ArchiveRestore, Trash2 } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'

const STATUS_VARIANT = {
  active: 'default',
  completed: 'secondary',
  archived: 'outline',
}

export default function CampaignListPage() {
  const navigate = useNavigate()
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showArchived, setShowArchived] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(null) // campaign id pending delete

  function load() {
    setError(null)
    return api.getCampaigns()
      .then(setCampaigns)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  async function archive(e, campaign) {
    e.stopPropagation()
    try {
      await api.patchCampaign(campaign.id, { status: 'archived' })
      load()
    } catch (e) { setError(e.message) }
  }

  async function unarchive(e, campaign) {
    e.stopPropagation()
    try {
      await api.patchCampaign(campaign.id, { status: 'active' })
      load()
    } catch (e) { setError(e.message) }
  }

  async function confirmDelete(e, campaign) {
    e.stopPropagation()
    setDeleteConfirm(campaign.id)
  }

  async function doDelete(e, id) {
    e.stopPropagation()
    try {
      await api.deleteCampaign(id)
      setDeleteConfirm(null)
      load()
    } catch (e) { setError(e.message) }
  }

  const visible = campaigns.filter((c) => showArchived || c.status !== 'archived')
  const archivedCount = campaigns.filter((c) => c.status === 'archived').length

  return (
    <div className="container max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Earthborne Rangers</h1>
        <Button onClick={() => navigate('/campaigns/new')}>
          <Plus className="h-4 w-4 mr-2" />
          New Campaign
        </Button>
      </div>

      {error && <ErrorMessage message={error} />}

      {loading && <LoadingSpinner />}

      {!loading && (
        <>
          {archivedCount > 0 && (
            <div className="flex justify-end mb-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowArchived((v) => !v)}
              >
                {showArchived
                  ? `Hide archived (${archivedCount})`
                  : `Show archived (${archivedCount})`}
              </Button>
            </div>
          )}

          {visible.length === 0 && (
            <div className="text-center py-16 text-muted-foreground">
              <p className="text-lg">No campaigns yet.</p>
              <p className="text-sm mt-1">Create your first campaign to get started.</p>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            {visible.map((c) => (
              <Card
                key={c.id}
                className={`cursor-pointer hover:shadow-md transition-shadow ${c.status === 'archived' ? 'opacity-60' : ''}`}
                onClick={() => c.status !== 'archived' && navigate(`/campaigns/${c.id}`)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-lg">{c.name}</CardTitle>
                    <Badge variant={STATUS_VARIANT[c.status] ?? 'outline'}>
                      {c.status}
                    </Badge>
                  </div>
                  <CardDescription>{c.storyline?.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  {c.current_day && c.status !== 'archived' && (
                    <p className="text-sm text-muted-foreground mb-3">
                      Day {c.current_day.day_number} — {c.current_day.weather}
                    </p>
                  )}

                  <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                    {c.status !== 'archived' ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-muted-foreground"
                        onClick={(e) => archive(e, c)}
                      >
                        <Archive className="h-3 w-3 mr-1" />
                        Archive
                      </Button>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-muted-foreground"
                        onClick={(e) => unarchive(e, c)}
                      >
                        <ArchiveRestore className="h-3 w-3 mr-1" />
                        Unarchive
                      </Button>
                    )}

                    {deleteConfirm === c.id ? (
                      <div className="flex items-center gap-1 ml-auto">
                        <span className="text-xs text-destructive">Delete permanently?</span>
                        <Button
                          variant="destructive"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={(e) => doDelete(e, c.id)}
                        >
                          Yes, delete
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm(null) }}
                        >
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-muted-foreground ml-auto"
                        onClick={(e) => confirmDelete(e, c)}
                      >
                        <Trash2 className="h-3 w-3 mr-1" />
                        Delete
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
