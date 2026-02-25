import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from '@/lib/api'

function mockFetch(status, body) {
  const response = {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(typeof body === 'string' ? body : JSON.stringify(body)),
  }
  return vi.fn().mockResolvedValue(response)
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('api.getCampaigns()', () => {
  it('calls GET /api/campaigns', async () => {
    global.fetch = mockFetch(200, [])
    await api.getCampaigns()
    expect(fetch).toHaveBeenCalledWith('/api/campaigns', expect.objectContaining({ method: 'GET' }))
  })

  it('returns parsed JSON', async () => {
    const data = [{ id: 1, name: 'Test Run' }]
    global.fetch = mockFetch(200, data)
    const result = await api.getCampaigns()
    expect(result).toEqual(data)
  })
})

describe('api.createCampaign()', () => {
  it('calls POST /api/campaigns with JSON body', async () => {
    global.fetch = mockFetch(201, { id: 1 })
    await api.createCampaign({ name: 'New', storyline_id: 1 })
    expect(fetch).toHaveBeenCalledWith(
      '/api/campaigns',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'New', storyline_id: 1 }),
      })
    )
  })
})

describe('api.deleteCampaign()', () => {
  it('returns null on 204', async () => {
    global.fetch = mockFetch(204, null)
    const result = await api.deleteCampaign(1)
    expect(result).toBeNull()
  })
})

describe('api.patchCampaign()', () => {
  it('calls PATCH /api/campaigns/:id', async () => {
    global.fetch = mockFetch(200, { id: 1, status: 'archived' })
    await api.patchCampaign(1, { status: 'archived' })
    expect(fetch).toHaveBeenCalledWith('/api/campaigns/1', expect.objectContaining({ method: 'PATCH' }))
  })
})

describe('api error handling', () => {
  it('throws on non-OK response', async () => {
    global.fetch = mockFetch(404, 'Not found')
    await expect(api.getCampaign(999)).rejects.toThrow()
  })
})

describe('api.getCards()', () => {
  it('appends query params when provided', async () => {
    global.fetch = mockFetch(200, [])
    await api.getCards({ card_type: 'personality', source_set: 'AWA' })
    const calledUrl = fetch.mock.calls[0][0]
    expect(calledUrl).toContain('card_type=personality')
    expect(calledUrl).toContain('source_set=AWA')
  })

  it('calls without query string when no params', async () => {
    global.fetch = mockFetch(200, [])
    await api.getCards()
    expect(fetch).toHaveBeenCalledWith('/api/cards', expect.anything())
  })
})

describe('api.revertTrade()', () => {
  it('calls POST on the revert sub-path', async () => {
    global.fetch = mockFetch(200, { id: 5, reverted: true })
    await api.revertTrade(1, 2, 5)
    expect(fetch).toHaveBeenCalledWith(
      '/api/campaigns/1/rangers/2/trades/5/revert',
      expect.objectContaining({ method: 'POST' })
    )
  })
})
