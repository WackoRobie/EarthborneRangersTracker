"""Tests for campaign rewards pool endpoints (free-form card names)."""

import pytest


@pytest.fixture
def reward(client, campaign):
    r = client.post(
        f"/api/campaigns/{campaign['id']}/rewards",
        json={"card_name": "Healing Salve", "quantity": 2},
    )
    assert r.status_code == 201
    return r.json()


class TestListRewards:
    def test_empty(self, client, campaign):
        r = client.get(f"/api/campaigns/{campaign['id']}/rewards")
        assert r.status_code == 200
        assert r.json() == []


class TestAddReward:
    def test_adds_reward(self, client, campaign):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rewards",
            json={"card_name": "Ember Stone", "quantity": 1},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["card_name"] == "Ember Stone"
        assert data["quantity"] == 1

    def test_trims_whitespace(self, client, campaign):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rewards",
            json={"card_name": "  Ember Stone  ", "quantity": 1},
        )
        assert r.status_code == 201
        assert r.json()["card_name"] == "Ember Stone"

    def test_increments_existing_by_name(self, client, campaign):
        """Adding the same card name again increases the quantity."""
        client.post(
            f"/api/campaigns/{campaign['id']}/rewards",
            json={"card_name": "Crystal Shard", "quantity": 1},
        )
        client.post(
            f"/api/campaigns/{campaign['id']}/rewards",
            json={"card_name": "Crystal Shard", "quantity": 2},
        )
        rewards = client.get(f"/api/campaigns/{campaign['id']}/rewards").json()
        crystal = next(r for r in rewards if r["card_name"] == "Crystal Shard")
        assert crystal["quantity"] == 3

    def test_empty_name_rejected(self, client, campaign):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rewards",
            json={"card_name": "   ", "quantity": 1},
        )
        assert r.status_code == 400

    def test_zero_quantity_rejected(self, client, campaign):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rewards",
            json={"card_name": "Valid Card", "quantity": 0},
        )
        assert r.status_code == 400

    def test_campaign_not_found(self, client):
        r = client.post(
            "/api/campaigns/9999/rewards",
            json={"card_name": "Ghost Card", "quantity": 1},
        )
        assert r.status_code == 404


class TestRemoveReward:
    def test_removes_reward(self, client, campaign, reward):
        r = client.delete(f"/api/campaigns/{campaign['id']}/rewards/{reward['id']}")
        assert r.status_code == 204
        remaining = client.get(f"/api/campaigns/{campaign['id']}/rewards").json()
        assert all(rw["id"] != reward["id"] for rw in remaining)

    def test_not_found(self, client, campaign):
        r = client.delete(f"/api/campaigns/{campaign['id']}/rewards/9999")
        assert r.status_code == 404

    def test_wrong_campaign(self, client, campaign, reward, storyline_id):
        """Cannot remove a reward through a different campaign."""
        other = client.post(
            "/api/campaigns", json={"name": "Other", "storyline_id": storyline_id}
        ).json()
        r = client.delete(f"/api/campaigns/{other['id']}/rewards/{reward['id']}")
        assert r.status_code == 404
