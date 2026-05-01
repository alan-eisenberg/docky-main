"""Tests for docky system monitoring module."""

import pytest
from docky.monitor import SystemMonitor
from docky.config import Config


class TestSystemMonitor:
    """Test system resource monitoring."""

    def test_cpu_info_returns_dict(self):
        config = Config()
        monitor = SystemMonitor(config)
        info = monitor.get_cpu_info()
        assert isinstance(info, dict)
        assert "cores" in info
        assert info["cores"] > 0

    def test_memory_info_returns_dict(self):
        config = Config()
        monitor = SystemMonitor(config)
        info = monitor.get_memory_info()
        assert isinstance(info, dict)
        assert "total_mb" in info

    def test_hugepages_status_returns_dict(self):
        config = Config()
        monitor = SystemMonitor(config)
        info = monitor.get_hugepages_status()
        assert isinstance(info, dict)
        assert "supported" in info

    def test_full_report(self):
        config = Config()
        monitor = SystemMonitor(config)
        report = monitor.get_full_report()
        assert "cpu" in report
        assert "memory" in report
        assert "hugepages" in report
