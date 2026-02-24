"""Tests for day endpoints (get day, close day)."""

import pytest


def _active_day(campaign):
    return next(d for d in campaign["days"] if d["status"] == "active")


def _close(client, campaign, location="The Valley", path="Forest"):
    day = _active_day(campaign)
    return client.post(
        f"/api/campaigns/{campaign['id']}/days/{day['id']}/close",
        json={"location": location, "path_terrain": path},
    )


class TestGetDay:
    def test_returns_day(self, client, campaign):
        day = _active_day(campaign)
        r = client.get(f"/api/campaigns/{campaign['id']}/days/{day['id']}")
        assert r.status_code == 200
        assert r.json()["day_number"] == 1

    def test_not_found(self, client, campaign):
        r = client.get(f"/api/campaigns/{campaign['id']}/days/9999")
        assert r.status_code == 404

    def test_wrong_campaign(self, client, campaign, storyline_id):
        """Day from a different campaign returns 404."""
        other = client.post(
            "/api/campaigns", json={"name": "Other", "storyline_id": storyline_id}
        ).json()
        other_day = _active_day(other)
        r = client.get(f"/api/campaigns/{campaign['id']}/days/{other_day['id']}")
        assert r.status_code == 404


class TestCloseDay:
    def test_closes_active_day(self, client, campaign):
        r = _close(client, campaign)
        assert r.status_code == 200
        closed = r.json()
        assert closed["status"] == "completed"
        assert closed["day_number"] == 1

    def test_advances_to_day_2(self, client, campaign):
        _close(client, campaign)
        r = client.get(f"/api/campaigns/{campaign['id']}")
        data = r.json()
        active = next(d for d in data["days"] if d["status"] == "active")
        assert active["day_number"] == 2

    def test_next_day_has_location(self, client, campaign):
        _close(client, campaign, location="Mountain Pass", path="Rocky Trail")
        r = client.get(f"/api/campaigns/{campaign['id']}")
        data = r.json()
        day_2 = next(d for d in data["days"] if d["day_number"] == 2)
        assert day_2["location"] == "Mountain Pass"
        assert day_2["path_terrain"] == "Rocky Trail"

    def test_cannot_close_non_active_day(self, client, campaign):
        """Trying to close a day that is not active returns 400."""
        upcoming = next(d for d in campaign["days"] if d["day_number"] == 2)
        r = client.post(
            f"/api/campaigns/{campaign['id']}/days/{upcoming['id']}/close",
            json={"location": "X", "path_terrain": "Y"},
        )
        assert r.status_code == 400

    def test_final_day_completes_campaign(self, client, campaign):
        """Closing the last (day 30) day marks the campaign completed."""
        # Fast-forward through all 29 preceding days
        detail = client.get(f"/api/campaigns/{campaign['id']}").json()
        for i in range(29):
            active = next(d for d in detail["days"] if d["status"] == "active")
            client.post(
                f"/api/campaigns/{campaign['id']}/days/{active['id']}/close",
                json={"location": "L", "path_terrain": "P"},
            )
            detail = client.get(f"/api/campaigns/{campaign['id']}").json()

        # Now close day 30
        active = next(d for d in detail["days"] if d["status"] == "active")
        assert active["day_number"] == 30
        client.post(
            f"/api/campaigns/{campaign['id']}/days/{active['id']}/close",
            json={"location": "End", "path_terrain": "Flat"},
        )
        final = client.get(f"/api/campaigns/{campaign['id']}").json()
        assert final["status"] == "completed"
