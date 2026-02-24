import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import PageHeader from '@/components/shared/PageHeader'
import LoadingSpinner from '@/components/shared/LoadingSpinner'
import ErrorMessage from '@/components/shared/ErrorMessage'

const ASPECTS = ['AWA', 'FIT', 'FOC', 'SPI']
const BG_SETS = ['Artisan', 'Forager', 'Shepherd', 'Traveler']
const SP_SETS = ['Artificer', 'Conciliator', 'Explorer', 'Shaper']
const STEPS = ['Aspect', 'Name', 'Personality', 'Background', 'Specialty', 'Outside Interest', 'Review']

function StepIndicator({ current }) {
  return (
    <div className="flex gap-1 mb-6 flex-wrap">
      {STEPS.map((s, i) => (
        <Badge
          key={s}
          variant={i === current ? 'default' : i < current ? 'secondary' : 'outline'}
          className="text-xs"
        >
          {i + 1}. {s}
        </Badge>
      ))}
    </div>
  )
}

function CardSelect({ label, cards, value, onChange, disabled }) {
  return (
    <div className="space-y-1">
      <Label className="text-xs">{label}</Label>
      <Select value={value ? String(value) : ''} onValueChange={(v) => onChange(parseInt(v))} disabled={disabled}>
        <SelectTrigger>
          <SelectValue placeholder="Select card..." />
        </SelectTrigger>
        <SelectContent>
          {cards.map((c) => (
            <SelectItem key={c.id} value={String(c.id)}>
              {c.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

export default function RangerCreatePage() {
  const { id: cid } = useParams()
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [allCards, setAllCards] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  // Form state
  const [aspectCardId, setAspectCardId] = useState(null)
  const [aspectCardName, setAspectCardName] = useState('')
  const [stats, setStats] = useState({ AWA: '', FIT: '', FOC: '', SPI: '' })
  const [name, setName] = useState('')
  const [personalityIds, setPersonalityIds] = useState({ AWA: null, FIT: null, FOC: null, SPI: null })
  const [backgroundSet, setBackgroundSet] = useState('')
  const [backgroundIds, setBackgroundIds] = useState([null, null, null, null, null])
  const [specialtySet, setSpecialtySet] = useState('')
  const [specialtyIds, setSpecialtyIds] = useState([null, null, null, null, null])
  const [roleCardId, setRoleCardId] = useState(null)
  const [outsideInterestId, setOutsideInterestId] = useState(null)

  useEffect(() => {
    api.getCards()
      .then(setAllCards)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const selectedAspectCard = allCards.find((c) => c.id === aspectCardId)

  const personalityByAspect = useMemo(() => {
    const map = {}
    ASPECTS.forEach((asp) => {
      map[asp] = allCards.filter((c) => c.card_type === 'personality' && c.source_set === asp)
    })
    return map
  }, [allCards])

  const bgCards = useMemo(() =>
    backgroundSet ? allCards.filter((c) => c.card_type === 'background' && c.source_set === backgroundSet) : [],
    [allCards, backgroundSet])

  const spCards = useMemo(() =>
    specialtySet ? allCards.filter((c) => c.card_type === 'specialty' && c.source_set === specialtySet) : [],
    [allCards, specialtySet])

  const roleCards = useMemo(() =>
    specialtySet ? allCards.filter((c) => c.card_type === 'role' && c.source_set === specialtySet) : [],
    [allCards, specialtySet])

  // Outside interest: non-expert background or specialty, not already chosen
  const chosenIds = new Set([
    ...backgroundIds.filter(Boolean),
    ...specialtyIds.filter(Boolean),
    roleCardId,
  ].filter(Boolean))

  const outsideInterestCards = useMemo(() =>
    allCards.filter((c) =>
      (c.card_type === 'background' || c.card_type === 'specialty') &&
      !c.is_expert &&
      c.card_type !== 'role' &&
      !chosenIds.has(c.id)
    ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [allCards, backgroundIds, specialtyIds, roleCardId])

  function setBackgroundId(index, val) {
    setBackgroundIds((prev) => { const n = [...prev]; n[index] = val; return n })
  }
  function setSpecialtyId(index, val) {
    setSpecialtyIds((prev) => { const n = [...prev]; n[index] = val; return n })
  }

  const canNext = [
    // 0 Aspect
    !!aspectCardName.trim() && ASPECTS.every((a) => stats[a] !== '' && !isNaN(parseInt(stats[a]))),
    // 1 Name
    !!name.trim(),
    // 2 Personality
    ASPECTS.every((a) => personalityIds[a]),
    // 3 Background
    !!backgroundSet && backgroundIds.every(Boolean),
    // 4 Specialty
    !!specialtySet && specialtyIds.every(Boolean) && !!roleCardId,
    // 5 Outside Interest
    !!outsideInterestId,
    // 6 Review
    true,
  ]

  async function handleSubmit() {
    setSubmitting(true)
    setError(null)
    try {
      await api.createRanger(cid, {
        name: name.trim(),
        aspect_card_name: aspectCardName.trim(),
        awa: parseInt(stats.AWA),
        fit: parseInt(stats.FIT),
        foc: parseInt(stats.FOC),
        spi: parseInt(stats.SPI),
        personality_card_ids: ASPECTS.map((a) => personalityIds[a]),
        background_set: backgroundSet,
        background_card_ids: backgroundIds,
        specialty_set: specialtySet,
        specialty_card_ids: specialtyIds,
        role_card_id: roleCardId,
        outside_interest_card_id: outsideInterestId,
      })
      navigate(`/campaigns/${cid}`)
    } catch (e) {
      setError(e.message)
      setSubmitting(false)
    }
  }

  if (loading) return <div className="container max-w-2xl mx-auto p-6"><LoadingSpinner /></div>

  const cardById = Object.fromEntries(allCards.map((c) => [c.id, c]))

  return (
    <div className="container max-w-2xl mx-auto p-6">
      <PageHeader title="Add Ranger" backTo={`/campaigns/${cid}`} />
      <StepIndicator current={step} />

      {error && <ErrorMessage message={error} />}

      <Card>
        <CardHeader>
          <CardTitle>{STEPS[step]}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">

          {/* Step 0 — Aspect */}
          {step === 0 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Enter the aspect card name printed on the card, then enter the four stat values shown on it.
              </p>
              <div className="space-y-2">
                <Label htmlFor="aspect-name">Aspect Card Name</Label>
                <Input
                  id="aspect-name"
                  placeholder="e.g. Wanderer"
                  value={aspectCardName}
                  onChange={(e) => setAspectCardName(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-4 gap-2">
                {ASPECTS.map((a) => (
                  <div key={a} className="space-y-1">
                    <Label className="text-xs">{a}</Label>
                    <Input
                      type="number"
                      min="0"
                      max="5"
                      value={stats[a]}
                      onChange={(e) => setStats((prev) => ({ ...prev, [a]: e.target.value }))}
                      className="text-center"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step 1 — Name */}
          {step === 1 && (
            <div className="space-y-2">
              <Label htmlFor="ranger-name">Ranger Name</Label>
              <Input
                id="ranger-name"
                placeholder="Enter ranger name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          )}

          {/* Step 2 — Personality */}
          {step === 2 && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Select one personality card for each aspect (×2 copies each → 8 cards).
              </p>
              {ASPECTS.map((asp) => (
                <CardSelect
                  key={asp}
                  label={`${asp} Personality`}
                  cards={personalityByAspect[asp]}
                  value={personalityIds[asp]}
                  onChange={(v) => setPersonalityIds((prev) => ({ ...prev, [asp]: v }))}
                />
              ))}
            </div>
          )}

          {/* Step 3 — Background */}
          {step === 3 && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Choose a background set, then pick 5 cards (×2 copies each → 10 cards).
              </p>
              <div className="space-y-1">
                <Label>Background Set</Label>
                <Select value={backgroundSet} onValueChange={(v) => { setBackgroundSet(v); setBackgroundIds([null,null,null,null,null]) }}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select set..." />
                  </SelectTrigger>
                  <SelectContent>
                    {BG_SETS.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              {backgroundSet && bgCards.length > 0 && (
                <>
                  {[0,1,2,3,4].map((i) => (
                    <CardSelect
                      key={i}
                      label={`Card ${i + 1}`}
                      cards={bgCards.filter((c) => c.id === backgroundIds[i] || !backgroundIds.includes(c.id))}
                      value={backgroundIds[i]}
                      onChange={(v) => setBackgroundId(i, v)}
                    />
                  ))}
                </>
              )}
            </div>
          )}

          {/* Step 4 — Specialty */}
          {step === 4 && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Choose a specialty set, pick 5 cards (×2 each → 10 cards), and pick 1 role card (starts in play).
              </p>
              <div className="space-y-1">
                <Label>Specialty Set</Label>
                <Select value={specialtySet} onValueChange={(v) => { setSpecialtySet(v); setSpecialtyIds([null,null,null,null,null]); setRoleCardId(null) }}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select set..." />
                  </SelectTrigger>
                  <SelectContent>
                    {SP_SETS.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              {specialtySet && spCards.length > 0 && (
                <>
                  {[0,1,2,3,4].map((i) => (
                    <CardSelect
                      key={i}
                      label={`Card ${i + 1}`}
                      cards={spCards.filter((c) => c.id === specialtyIds[i] || !specialtyIds.includes(c.id))}
                      value={specialtyIds[i]}
                      onChange={(v) => setSpecialtyId(i, v)}
                    />
                  ))}
                  <CardSelect
                    label="Role Card (starts in play)"
                    cards={roleCards}
                    value={roleCardId}
                    onChange={setRoleCardId}
                  />
                </>
              )}
            </div>
          )}

          {/* Step 5 — Outside Interest */}
          {step === 5 && (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Pick 1 outside interest card (non-expert background or specialty, ×2 → 2 cards).
                Cannot be a card already chosen.
              </p>
              <CardSelect
                label="Outside Interest"
                cards={outsideInterestCards}
                value={outsideInterestId}
                onChange={setOutsideInterestId}
              />
            </div>
          )}

          {/* Step 6 — Review */}
          {step === 6 && (
            <div className="space-y-3 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <p className="text-muted-foreground">Name</p>
                  <p className="font-medium">{name}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Aspect</p>
                  <p className="font-medium">{aspectCardName}</p>
                  <p className="text-xs text-muted-foreground">AWA {stats.AWA} / FIT {stats.FIT} / FOC {stats.FOC} / SPI {stats.SPI}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Background Set</p>
                  <p className="font-medium">{backgroundSet}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Specialty Set</p>
                  <p className="font-medium">{specialtySet}</p>
                </div>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Personality Cards (×2 each)</p>
                <ul className="list-disc list-inside">
                  {ASPECTS.map((a) => personalityIds[a] && (
                    <li key={a}>{cardById[personalityIds[a]]?.name} ({a})</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Background Cards (×2 each)</p>
                <ul className="list-disc list-inside">
                  {backgroundIds.filter(Boolean).map((id, i) => (
                    <li key={i}>{cardById[id]?.name}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Specialty Cards (×2 each)</p>
                <ul className="list-disc list-inside">
                  {specialtyIds.filter(Boolean).map((id, i) => (
                    <li key={i}>{cardById[id]?.name}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-muted-foreground">Role Card (in play)</p>
                <p className="font-medium">{cardById[roleCardId]?.name}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Outside Interest (×2)</p>
                <p className="font-medium">{cardById[outsideInterestId]?.name}</p>
              </div>
              <p className="text-muted-foreground font-medium">Starting deck: 30 cards</p>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-between mt-4">
        <Button variant="outline" onClick={() => setStep((s) => s - 1)} disabled={step === 0}>
          Back
        </Button>
        {step < STEPS.length - 1 ? (
          <Button onClick={() => setStep((s) => s + 1)} disabled={!canNext[step]}>
            Next
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={submitting || !canNext[step]}>
            {submitting ? 'Creating...' : 'Create Ranger'}
          </Button>
        )}
      </div>
    </div>
  )
}
