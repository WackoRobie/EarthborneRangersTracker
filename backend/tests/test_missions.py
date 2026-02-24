"""Tests for mission endpoints."""

import pytest


@pytest.fixture
def active_day_id(campaign):
    return next(d for d in campaign["days"] if d["status"] == "active")["id"]


@pytest.fixture
def mission(client, campaign, active_day_id):
    r = client.post(
        f"/api/campaigns/{campaign['id']}/missions",
        json={"name": "Restore the grove", "max_progress": 3},
    )
    assert r.status_code == 201
    return r.json()


class TestListMissions:
    def test_empty(self, client, campaign):
        r = client.get(f"/api/campaigns/{campaign['id']}/missions")
        assert r.status_code == 200
        assert r.json() == []


class TestCreateMission:
    def test_creates_mission(self, client, campaign):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/missions",
            json={"name": "Find the relic", "max_progress": 2},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Find the relic"
        assert data["max_progress"] == 2
        assert data["progress"] == 0

    def test_defaults_day_started_to_active_day(self, client, campaign, active_day_id):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/missions",
            json={"name": "Test mission", "max_progress": 1},
        )
        assert r.json()["day_started_id"] == active_day_id

    def test_pass_fail_mission(self, client, campaign):
        """max_progress=0 means pass/fail only."""
        r = client.post(
            f"/api/campaigns/{campaign['id']}/missions",
            json={"name": "Survive", "max_progress": 0},
        )
        assert r.status_code == 201
        assert r.json()["max_progress"] == 0

    def test_max_progress_out_of_range(self, client, campaign):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/missions",
            json={"name": "Bad mission", "max_progress": 4},
        )
        assert r.status_code == 400

    def test_campaign_not_found(self, client):
        r = client.post(
            "/api/campaigns/9999/missions",
            json={"name": "Ghost mission", "max_progress": 1},
        )
        assert r.status_code == 404


class TestUpdateMission:
    def test_update_progress(self, client, campaign, mission):
        r = client.patch(
            f"/api/campaigns/{campaign['id']}/missions/{mission['id']}",
            json={"progress": 2},
        )
        assert r.status_code == 200
        assert r.json()["progress"] == 2

    def test_progress_cannot_exceed_max(self, client, campaign, mission):
        r = client.patch(
            f"/api/campaigns/{campaign['id']}/missions/{mission['id']}",
            json={"progress": 4},  # max_progress is 3
        )
        assert r.status_code == 400

    def test_progress_cannot_be_negative(self, client, campaign, mission):
        r = client.patch(
            f"/api/campaigns/{campaign['id']}/missions/{mission['id']}",
            json={"progress": -1},
        )
        assert r.status_code == 400

    def test_mark_completed(self, client, campaign, mission, active_day_id):
        r = client.patch(
            f"/api/campaigns/{campaign['id']}/missions/{mission['id']}",
            json={"progress": 3, "day_completed_id": active_day_id},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["progress"] == 3
        assert data["day_completed_id"] == active_day_id

    def test_mission_not_found(self, client, campaign):
        r = client.patch(
            f"/api/campaigns/{campaign['id']}/missions/9999",
            json={"progress": 1},
        )
        assert r.status_code == 404
