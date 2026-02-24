import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { RotateCcw } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import PageHeader from '@/components/shared/PageHeader'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'

function StatBadge({ label, value }) {
  return (
    <div className="flex flex-col items-center p-3 rounded-md bg-muted min-w-[60px]">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-xl font-bold">{value}</span>
    </div>
  )
}

function DeckSection({ title, entries }) {
  if (!entries || entries.length === 0) return null
  return (
    <div>
      <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
      <ul className="space-y-1">
        {entries.map((e, i) => (
          <li key={i} className="flex justify-between text-sm">
            <span>{e.card.name}</span>
            <span className="text-muted-foreground">×{e.quantity}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function RangerDetailPage() {
  const { id: cid, rangerId } = useParams()
  const [ranger, setRanger] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadRanger = useCallback(() => {
    return api.getRanger(cid, rangerId)
      .then(setRanger)
      .catch((e) => setError(e.message))
  }, [cid, rangerId])

  useEffect(() => {
    loadRanger().finally(() => setLoading(false))
  }, [loadRanger])

  async function revertTrade(tid) {
    try {
      await api.revertTrade(cid, rangerId, tid)
      loadRanger()
    } catch (e) { setError(e.message) }
  }

  if (loading) return <div className="container max-w-2xl mx-auto p-6"><LoadingSpinner /></div>
  if (error) return <div className="container max-w-2xl mx-auto p-6"><ErrorMessage message={error} /></div>
  if (!ranger) return null

  const decklist = ranger.current_decklist ?? []
  const trades = ranger.trades ?? []

  // Group decklist by card type
  const personality = decklist.filter((e) => e.card.card_type === 'personality')
  const background = decklist.filter((e) => e.card.card_type === 'background')
  const specialty = decklist.filter((e) => e.card.card_type === 'specialty')
  const outside = decklist.filter((e) => e.card.id === ranger.outside_interest_card?.id)
  const role = decklist.filter((e) => e.card.card_type === 'role')

  const nonReverted = trades.filter((t) => !t.reverted)
  const reverted = trades.filter((t) => t.reverted)

  return (
    <div className="container max-w-2xl mx-auto p-6">
      <PageHeader title={ranger.name} backTo={`/campaigns/${cid}`} />

      {error && <ErrorMessage message={error} />}

      {/* Stats */}
      <Card className="mb-6">
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-3 mb-3">
            <StatBadge label="AWA" value={ranger.awa} />
            <StatBadge label="FIT" value={ranger.fit} />
            <StatBadge label="FOC" value={ranger.foc} />
            <StatBadge label="SPI" value={ranger.spi} />
          </div>
          <p className="text-sm text-muted-foreground">
            Aspect: <span className="font-medium text-foreground">{ranger.aspect_card_name}</span>
          </p>
          <p className="text-sm text-muted-foreground">
            Background: <span className="font-medium text-foreground">{ranger.background_set}</span> ·
            Specialty: <span className="font-medium text-foreground">{ranger.specialty_set}</span>
          </p>
        </CardContent>
      </Card>

      {/* Decklist */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">
            Current Deck
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              ({decklist.reduce((s, e) => s + e.quantity, 0)} cards)
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {role.length > 0 && (
            <>
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Role (in play)</p>
                <ul className="space-y-1">
                  {role.map((e, i) => (
                    <li key={i} className="text-sm">{e.name}</li>
                  ))}
                </ul>
              </div>
              <Separator />
            </>
          )}
          <DeckSection title="Personality (×2 each)" entries={personality} />
          <DeckSection title="Background" entries={background} />
          <DeckSection title="Specialty" entries={specialty} />
          <DeckSection title="Outside Interest (×2)" entries={outside} />
        </CardContent>
      </Card>

      {/* Trade History */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Trade History</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {trades.length === 0 && (
            <p className="text-sm text-muted-foreground">No trades recorded.</p>
          )}

          {nonReverted.map((t) => (
            <div key={t.id} className="flex items-center justify-between text-sm">
              <span>
                <span className="text-muted-foreground">{t.original_card?.name}</span>
                {' → '}
                <span className="font-medium">{t.reward_card?.name}</span>
              </span>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => revertTrade(t.id)}
                title="Revert trade">
                <RotateCcw className="h-3 w-3" />
              </Button>
            </div>
          ))}

          {reverted.length > 0 && (
            <>
              <Separator />
              <p className="text-xs text-muted-foreground">Reverted trades</p>
              {reverted.map((t) => (
                <div key={t.id} className="flex items-center justify-between text-sm opacity-50">
                  <span className="line-through">
                    {t.original_card?.name} → {t.reward_card?.name}
                  </span>
                  <Badge variant="outline" className="text-xs">reverted</Badge>
                </div>
              ))}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
