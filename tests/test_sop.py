import pytest
from src.sop.engine import SOPEngine


@pytest.fixture
def engine():
    e = SOPEngine()
    e.load_all()
    return e


class TestSOPEngine:
    def test_load_sops(self, engine):
        assert len(engine._sops) >= 6
        assert "FLIGHT_REFUND_DISPUTE" in engine._sops

    def test_exact_match_flight(self, engine):
        result = engine.search("机票", "退差价")
        assert result["matched"] is True
        assert result["match_confidence"] == 1.0
        assert result["sop"]["id"] == "FLIGHT_REFUND_DISPUTE"

    def test_exact_match_hotel(self, engine):
        result = engine.search("酒店", "取消预订")
        assert result["matched"] is True
        assert result["match_confidence"] == 1.0
        assert result["sop"]["id"] == "HOTEL_CANCELLATION"

    def test_exact_match_ride(self, engine):
        result = engine.search("打车", "司机迟到")
        assert result["matched"] is True
        assert result["match_confidence"] == 1.0
        assert result["sop"]["id"] == "RIDE_DRIVER_LATE"

    def test_exact_match_train(self, engine):
        result = engine.search("火车", "改签")
        assert result["matched"] is True
        assert result["match_confidence"] == 1.0
        assert result["sop"]["id"] == "TRAIN_TICKET_CHANGE"

    def test_no_match_unknown_issue(self, engine):
        result = engine.search("打车", "行李遗失")
        assert result["matched"] is True
        assert result["match_confidence"] == 0.5

    def test_no_match_unknown_category(self, engine):
        result = engine.search("游轮", "退票")
        assert result["matched"] is False

    def test_sop_has_templates(self, engine):
        result = engine.search("机票", "退差价")
        sop = result["sop"]
        assert "templates" in sop
        assert len(sop["templates"]) > 0

    def test_sop_has_actions(self, engine):
        result = engine.search("打车", "司机迟到")
        sop = result["sop"]
        assert "suggested_actions" in sop
        assert len(sop["suggested_actions"]) > 0

    def test_list_sops(self, engine):
        sops = engine.list_sops()
        assert len(sops) >= 6
        ids = {s["id"] for s in sops}
        assert "FLIGHT_REFUND_DISPUTE" in ids
        assert "RIDE_DRIVER_LATE" in ids

    def test_reload(self, engine):
        result = engine.reload()
        assert result["status"] == "reloaded"
        assert result["sop_count"] >= 6
