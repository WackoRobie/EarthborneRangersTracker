const base = '/api'

async function req(method, path, body) {
  const res = await fetch(`${base}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.status === 204 ? null : res.json()
}

export const api = {
  // campaigns
  getCampaigns: () => req('GET', '/campaigns'),
  createCampaign: (body) => req('POST', '/campaigns', body),
  getCampaign: (id) => req('GET', `/campaigns/${id}`),
  patchCampaign: (id, body) => req('PATCH', `/campaigns/${id}`, body),
  deleteCampaign: (id) => req('DELETE', `/campaigns/${id}`),
  // days
  getDays: (cid) => req('GET', `/campaigns/${cid}/days`),
  getDay: (cid, did) => req('GET', `/campaigns/${cid}/days/${did}`),
  closeDay: (cid, did, body) => req('POST', `/campaigns/${cid}/days/${did}/close`, body),
  // rangers
  getRangers: (cid) => req('GET', `/campaigns/${cid}/rangers`),
  createRanger: (cid, body) => req('POST', `/campaigns/${cid}/rangers`, body),
  getRanger: (cid, rid) => req('GET', `/campaigns/${cid}/rangers/${rid}`),
  createTrade: (cid, rid, body) => req('POST', `/campaigns/${cid}/rangers/${rid}/trades`, body),
  revertTrade: (cid, rid, tid) => req('POST', `/campaigns/${cid}/rangers/${rid}/trades/${tid}/revert`),
  // missions
  getMissions: (cid) => req('GET', `/campaigns/${cid}/missions`),
  createMission: (cid, body) => req('POST', `/campaigns/${cid}/missions`, body),
  patchMission: (cid, mid, body) => req('PATCH', `/campaigns/${cid}/missions/${mid}`, body),
  // events
  getEvents: (cid) => req('GET', `/campaigns/${cid}/events`),
  createEvent: (cid, body) => req('POST', `/campaigns/${cid}/events`, body),
  deleteEvent: (cid, eid) => req('DELETE', `/campaigns/${cid}/events/${eid}`),
  // rewards
  getRewards: (cid) => req('GET', `/campaigns/${cid}/rewards`),
  addReward: (cid, body) => req('POST', `/campaigns/${cid}/rewards`, body),
  removeReward: (cid, rwid) => req('DELETE', `/campaigns/${cid}/rewards/${rwid}`),
  // cards
  getCards: (params) => req('GET', `/cards${params ? '?' + new URLSearchParams(params) : ''}`),
  // storylines
  getStorylines: () => req('GET', '/storylines'),
}
