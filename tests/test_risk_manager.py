"""Tests for risk manager."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from database.seed_data import seed_database
from core.risk_manager import RiskManager


class TestRiskManager:
    """Test risk manager functionality."""

    def setup_method(self):
        """Setup test database."""
        self.db = DatabaseManager()
        self.db.create_tables()
        seed_database()
        self.session = self.db.get_session()
        self.risk_mgr = RiskManager(self.session)

    def teardown_method(self):
        """Cleanup."""
        self.session.close()

    def test_position_size_calculation(self):
        """Test position size calculation."""
        qty = self.risk_mgr.calculate_position_size(
            balance=10000, risk_percent=1.0,
            entry_price=64000, stop_loss=63500
        )
        assert qty > 0
        expected = (10000 * 0.01) / (64000 - 63500)
        assert abs(qty - expected) < 0.0001

    def test_position_size_zero_risk(self):
        """Test position size with zero risk."""
        qty = self.risk_mgr.calculate_position_size(
            balance=10000, risk_percent=1.0,
            entry_price=64000, stop_loss=64000
        )
        assert qty == 0.0

    def test_can_open_position(self):
        """Test if position can be opened."""
        result = self.risk_mgr.can_open_position("BTCUSDT", "LONG")
        assert result is True

    def test_daily_loss_check(self):
        """Test daily loss limit check."""
        result = self.risk_mgr.check_daily_loss_limit()
        assert result is True

    def test_signal_validation(self):
        """Test signal validation."""
        valid_signal = {
            "symbol": "BTCUSDT",
            "market": "crypto",
            "strategy": "day_trading",
            "signal_type": "LONG",
            "entry_price": 64000,
            "stop_loss": 63500,
        }
        assert self.risk_mgr.validate_signal(valid_signal) is True

        invalid_signal = {
            "symbol": "BTCUSDT",
            "market": "crypto",
            "strategy": "day_trading",
            "signal_type": "LONG",
            "entry_price": 64000,
            "stop_loss": 64500,  # SL above entry for LONG
        }
        assert self.risk_mgr.validate_signal(invalid_signal) is False

    def test_signal_validation_missing_fields(self):
        """Test signal validation with missing fields."""
        incomplete_signal = {
            "symbol": "BTCUSDT",
        }
        assert self.risk_mgr.validate_signal(incomplete_signal) is False


if __name__ == "__main__":
    test = TestRiskManager()
    test.setup_method()
    try:
        test.test_position_size_calculation()
        test.test_position_size_zero_risk()
        test.test_can_open_position()
        test.test_daily_loss_check()
        test.test_signal_validation()
        test.test_signal_validation_missing_fields()
        print("All risk manager tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        test.teardown_method()
