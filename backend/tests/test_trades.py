"""Tests for ranger trade (create + revert) endpoints.

Trade mechanics require a pool entry linked by card_id (not card_name).
We insert pool entries directly using the _adjust_pool path by first
creating a ranger (which uses card_ids internally).

To set up a valid trade:
  1. Create campaign + ranger
  2. Insert a pool entry via direct DB (using engine) with a card_id that
     exists in the seeded card library but is NOT in the ranger's deck
  3. Execute the trade via the API
"""

import pytest
from sqlalchemy import text


@pytest.fixture
def ranger(client, campaign, ranger_payload):
    r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def pool_card_id(card_ids):
    """A card not in the ranger's starting deck that can go into the pool."""
    return card_ids["Wrist-mounted Darter"]  # Artificer specialty, not chosen


@pytest.fixture
def deck_card_id(card_ids):
    """A card that IS in the ranger's starting deck (background Artisan card ×2)."""
    return card_ids["Universal Power Cells"]


@pytest.fixture
def pool_entry(engine, campaign, pool_card_id):
    """Insert a pool entry with card_id (FK-based) directly into the DB."""
    with engine.connect() as conn:
        conn.execute(
            text(
                "INSERT INTO campaign_rewards (campaign_id, card_id, quantity) "
                "VALUES (:cid, :card, 1)"
            ),
            {"cid": campaign["id"], "card": pool_card_id},
        )
        conn.commit()


@pytest.fixture
def active_day(campaign):
    return next(d for d in campaign["days"] if d["status"] == "active")


class TestCreateTrade:
    def test_creates_trade(self, client, campaign, ranger, pool_entry, pool_card_id, deck_card_id, active_day):
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades",
            json={
                "day_id": active_day["id"],
                "original_card_id": deck_card_id,
                "reward_card_id": pool_card_id,
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["reverted"] is False
        assert data["original_card"]["id"] == deck_card_id
        assert data["reward_card"]["id"] == pool_card_id

    def test_deck_updates_after_trade(self, client, campaign, ranger, pool_entry, pool_card_id, deck_card_id, active_day):
        """After a trade: original card quantity drops, reward card appears."""
        client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades",
            json={
                "day_id": active_day["id"],
                "original_card_id": deck_card_id,
                "reward_card_id": pool_card_id,
            },
        )
        r = client.get(f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}")
        deck = {e["card"]["id"]: e["quantity"] for e in r.json()["current_decklist"]}
        # original went from 2 → 1 (one copy traded away)
        assert deck[deck_card_id] == 1
        # reward card now in deck
        assert deck[pool_card_id] == 1

    def test_original_card_not_in_deck(self, client, campaign, ranger, pool_entry, pool_card_id, active_day, card_ids):
        """Using a card not in the deck as original returns 400."""
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades",
            json={
                "day_id": active_day["id"],
                "original_card_id": pool_card_id,  # pool card, not in deck
                "reward_card_id": pool_card_id,
            },
        )
        assert r.status_code == 400

    def test_reward_card_not_in_pool(self, client, campaign, ranger, active_day, deck_card_id, card_ids):
        """Using a card not in the pool as reward returns 400."""
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades",
            json={
                "day_id": active_day["id"],
                "original_card_id": deck_card_id,
                "reward_card_id": card_ids["Wrist-mounted Darter"],  # not in pool
            },
        )
        assert r.status_code == 400


class TestRevertTrade:
    def test_reverts_trade(self, client, campaign, ranger, pool_entry, pool_card_id, deck_card_id, active_day):
        trade = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades",
            json={
                "day_id": active_day["id"],
                "original_card_id": deck_card_id,
                "reward_card_id": pool_card_id,
            },
        ).json()

        r = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades/{trade['id']}/revert"
        )
        assert r.status_code == 200
        assert r.json()["reverted"] is True

    def test_deck_restored_after_revert(self, client, campaign, ranger, pool_entry, pool_card_id, deck_card_id, active_day):
        trade = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades",
            json={
                "day_id": active_day["id"],
                "original_card_id": deck_card_id,
                "reward_card_id": pool_card_id,
            },
        ).json()

        client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades/{trade['id']}/revert"
        )

        r = client.get(f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}")
        deck = {e["card"]["id"]: e["quantity"] for e in r.json()["current_decklist"]}
        # original card restored to ×2
        assert deck[deck_card_id] == 2
        # reward card removed from deck
        assert pool_card_id not in deck

    def test_cannot_revert_already_reverted(self, client, campaign, ranger, pool_entry, pool_card_id, deck_card_id, active_day):
        trade = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades",
            json={
                "day_id": active_day["id"],
                "original_card_id": deck_card_id,
                "reward_card_id": pool_card_id,
            },
        ).json()
        client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades/{trade['id']}/revert"
        )
        r = client.post(
            f"/api/campaigns/{campaign['id']}/rangers/{ranger['id']}/trades/{trade['id']}/revert"
        )
        assert r.status_code == 400
