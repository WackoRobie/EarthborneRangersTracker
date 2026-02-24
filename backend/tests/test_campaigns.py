"""Tests for campaign CRUD endpoints."""

import pytest


class TestListCampaigns:
    def test_empty(self, client):
        r = client.get("/api/campaigns")
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_created_campaigns(self, client, campaign):
        r = client.get("/api/campaigns")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Run"
        assert data[0]["status"] == "active"

    def test_includes_current_day(self, client, campaign):
        r = client.get("/api/campaigns")
        data = r.json()
        assert data[0]["current_day"] is not None
        assert data[0]["current_day"]["day_number"] == 1
        assert data[0]["current_day"]["weather"] == "A Perfect Day"


class TestCreateCampaign:
    def test_creates_with_30_days(self, client, storyline_id):
        r = client.post("/api/campaigns", json={"name": "New Run", "storyline_id": storyline_id})
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "New Run"
        assert data["status"] == "active"
        assert len(data["days"]) == 30

    def test_day_one_is_active(self, client, storyline_id):
        r = client.post("/api/campaigns", json={"name": "New Run", "storyline_id": storyline_id})
        days = r.json()["days"]
        active = [d for d in days if d["status"] == "active"]
        assert len(active) == 1
        assert active[0]["day_number"] == 1

    def test_storyline_not_found(self, client):
        r = client.post("/api/campaigns", json={"name": "Bad Run", "storyline_id": 9999})
        assert r.status_code == 404


class TestGetCampaign:
    def test_returns_detail(self, client, campaign):
        r = client.get(f"/api/campaigns/{campaign['id']}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == campaign["id"]
        assert "days" in data
        assert "missions" in data
        assert "rewards" in data
        assert "notable_events" in data

    def test_not_found(self, client):
        r = client.get("/api/campaigns/9999")
        assert r.status_code == 404


class TestUpdateCampaign:
    def test_rename(self, client, campaign):
        r = client.patch(f"/api/campaigns/{campaign['id']}", json={"name": "Renamed"})
        assert r.status_code == 200
        assert r.json()["name"] == "Renamed"

    def test_archive(self, client, campaign):
        r = client.patch(f"/api/campaigns/{campaign['id']}", json={"status": "archived"})
        assert r.status_code == 200
        assert r.json()["status"] == "archived"

    def test_complete(self, client, campaign):
        r = client.patch(f"/api/campaigns/{campaign['id']}", json={"status": "completed"})
        assert r.status_code == 200
        assert r.json()["status"] == "completed"

    def test_invalid_status(self, client, campaign):
        r = client.patch(f"/api/campaigns/{campaign['id']}", json={"status": "deleted"})
        assert r.status_code == 400

    def test_not_found(self, client):
        r = client.patch("/api/campaigns/9999", json={"name": "X"})
        assert r.status_code == 404


class TestDeleteCampaign:
    def test_deletes_campaign(self, client, campaign):
        r = client.delete(f"/api/campaigns/{campaign['id']}")
        assert r.status_code == 204
        # Confirm gone
        r2 = client.get(f"/api/campaigns/{campaign['id']}")
        assert r2.status_code == 404

    def test_not_found(self, client):
        r = client.delete("/api/campaigns/9999")
        assert r.status_code == 404

    def test_cascade_deletes_days(self, client, campaign):
        """Deleting a campaign should cascade to its days (no orphan errors)."""
        r = client.delete(f"/api/campaigns/{campaign['id']}")
        assert r.status_code == 204
