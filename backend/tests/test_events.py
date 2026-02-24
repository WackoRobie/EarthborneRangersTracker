"""Tests for notable event endpoints."""

import pytest


@pytest.fixture
def active_day_id(campaign):
    return next(d for d in campaign["days"] if d["status"] == "active")["id"]


@pytest.fixture
def event(client, campaign, active_day_id):
    r = client.post(
        f"/api/campaigns/{campaign['id']}/events",
        json={"day_id": active_day_id, "text": "A wolf pack was spotted near the ridge."},
    )
    assert r.status_code == 201
    return r.json()


class TestListEvents:
    def test_empty(self, client, campaign):
        r = client.get(f"/api/campaigns/{campaign['id']}/events")
        assert r.status_code == 200
        assert r.json() == []


class TestCreateEvent:
    def test_creates_event(self, client, campaign, active_day_id):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/events",
            json={"day_id": active_day_id, "text": "We found an old camp."},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["text"] == "We found an old camp."
        assert data["day_id"] == active_day_id

    def test_day_not_in_campaign(self, client, campaign, storyline_id):
        """A day_id from a different campaign returns 400."""
        other = client.post(
            "/api/campaigns", json={"name": "Other", "storyline_id": storyline_id}
        ).json()
        other_day_id = next(d for d in other["days"] if d["status"] == "active")["id"]
        r = client.post(
            f"/api/campaigns/{campaign['id']}/events",
            json={"day_id": other_day_id, "text": "Cross-campaign event."},
        )
        assert r.status_code == 400

    def test_campaign_not_found(self, client, active_day_id):
        r = client.post(
            "/api/campaigns/9999/events",
            json={"day_id": active_day_id, "text": "Ghost event."},
        )
        assert r.status_code == 404


class TestDeleteEvent:
    def test_deletes_event(self, client, campaign, event):
        r = client.delete(f"/api/campaigns/{campaign['id']}/events/{event['id']}")
        assert r.status_code == 204
        events = client.get(f"/api/campaigns/{campaign['id']}/events").json()
        assert all(e["id"] != event["id"] for e in events)

    def test_not_found(self, client, campaign):
        r = client.delete(f"/api/campaigns/{campaign['id']}/events/9999")
        assert r.status_code == 404

    def test_wrong_campaign(self, client, campaign, event, storyline_id):
        """Cannot delete an event through a different campaign."""
        other = client.post(
            "/api/campaigns", json={"name": "Other", "storyline_id": storyline_id}
        ).json()
        r = client.delete(f"/api/campaigns/{other['id']}/events/{event['id']}")
        assert r.status_code == 404
