"""Tests for ranger creation and retrieval."""

import pytest


class TestListRangers:
    def test_empty(self, client, campaign):
        r = client.get(f"/api/campaigns/{campaign['id']}/rangers")
        assert r.status_code == 200
        assert r.json() == []


class TestCreateRanger:
    def test_creates_ranger(self, client, campaign, ranger_payload):
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Aria"
        assert data["awa"] == 2
        assert data["fit"] == 3

    def test_starting_deck_size_30(self, client, campaign, ranger_payload):
        """Starting deck = 4×2 (personality) + 5×2 (background) + 5×2 (specialty) + 1×2 (OI) = 30."""
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
        deck = r.json()["current_decklist"]
        total = sum(e["quantity"] for e in deck)
        assert total == 30

    def test_role_card_not_in_deck(self, client, campaign, ranger_payload, card_ids):
        """The role card is in-play but should not appear in the decklist."""
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
        deck_ids = {e["card"]["id"] for e in r.json()["current_decklist"]}
        assert card_ids["Masterful Engineer"] not in deck_ids

    def test_outside_interest_in_deck(self, client, campaign, ranger_payload, card_ids):
        """Outside interest card appears ×2."""
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
        oi_entries = [
            e for e in r.json()["current_decklist"]
            if e["card"]["id"] == card_ids["Familiar Ground"]
        ]
        assert len(oi_entries) == 1
        assert oi_entries[0]["quantity"] == 2

    def test_personality_cards_appear_twice(self, client, campaign, ranger_payload, card_ids):
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
        deck = {e["card"]["id"]: e["quantity"] for e in r.json()["current_decklist"]}
        assert deck[card_ids["Insightful"]] == 2
        assert deck[card_ids["Meticulous"]] == 2

    def test_wrong_background_set(self, client, campaign, ranger_payload, card_ids):
        bad = dict(ranger_payload)
        bad["background_set"] = "BadSet"
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=bad)
        assert r.status_code == 400

    def test_wrong_number_of_background_cards(self, client, campaign, ranger_payload):
        bad = dict(ranger_payload)
        bad["background_card_ids"] = ranger_payload["background_card_ids"][:4]
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=bad)
        assert r.status_code == 400

    def test_duplicate_background_cards(self, client, campaign, ranger_payload):
        bad = dict(ranger_payload)
        bad["background_card_ids"] = ranger_payload["background_card_ids"][:4] + [
            ranger_payload["background_card_ids"][0]
        ]
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=bad)
        assert r.status_code == 400

    def test_wrong_personality_aspect(self, client, campaign, ranger_payload, card_ids):
        """Two AWA personality cards — missing FIT → error."""
        bad = dict(ranger_payload)
        bad["personality_card_ids"] = [
            card_ids["Insightful"],   # AWA
            card_ids["Vigilant"],     # AWA (duplicate aspect)
            card_ids["Meticulous"],   # FOC
            card_ids["Persuasive"],   # SPI
        ]
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=bad)
        assert r.status_code == 400

    def test_expert_card_as_outside_interest(self, client, campaign, ranger_payload, card_ids):
        """Expert-trait cards cannot be used as outside interest."""
        bad = dict(ranger_payload)
        bad["outside_interest_card_id"] = card_ids["Masterwork"]  # Artisan expert
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=bad)
        assert r.status_code == 400

    def test_role_card_not_valid_as_specialty(self, client, campaign, ranger_payload, card_ids):
        """Including a role card in specialty_card_ids is rejected."""
        bad = dict(ranger_payload)
        bad["specialty_card_ids"] = ranger_payload["specialty_card_ids"][:4] + [
            card_ids["Masterful Engineer"]
        ]
        r = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=bad)
        assert r.status_code == 400

    def test_campaign_card_uniqueness(self, client, campaign, ranger_payload):
        """Creating a second ranger with overlapping cards is rejected."""
        r1 = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
        assert r1.status_code == 201
        r2 = client.post(f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload)
        assert r2.status_code == 400

    def test_campaign_not_found(self, client, ranger_payload):
        r = client.post("/api/campaigns/9999/rangers", json=ranger_payload)
        assert r.status_code == 404


class TestGetRanger:
    def test_returns_ranger(self, client, campaign, ranger_payload):
        created = client.post(
            f"/api/campaigns/{campaign['id']}/rangers", json=ranger_payload
        ).json()
        r = client.get(f"/api/campaigns/{campaign['id']}/rangers/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_not_found(self, client, campaign):
        r = client.get(f"/api/campaigns/{campaign['id']}/rangers/9999")
        assert r.status_code == 404
