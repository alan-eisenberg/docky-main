"""Tests for docky service discovery module."""

import pytest
from docky.discovery import ServiceDiscovery
from docky.config import Config


class TestServiceDiscovery:
    """Test service discovery and health checking."""

    def test_parse_address(self):
        host, port = ServiceDiscovery._parse_addr("example.com:3333")
        assert host == "example.com"
        assert port == 3333

    def test_parse_address_with_subdomain(self):
        host, port = ServiceDiscovery._parse_addr("eu.node-alpha.net:443")
        assert host == "eu.node-alpha.net"
        assert port == 443

    def test_tcp_check_unreachable(self):
        # Should fail on a non-routable address
        result = ServiceDiscovery._check_tcp("192.0.2.1", 19999, timeout=1)
        assert result is False

    def test_discovery_initialization(self):
        config = Config()
        discovery = ServiceDiscovery(config)
        assert discovery.get_available_count() == 0
        assert discovery.get_unreachable_count() == 0

    def test_status_report_format(self):
        config = Config()
        discovery = ServiceDiscovery(config)
        report = discovery.get_status_report()
        assert "reachable" in report
        assert "unreachable" in report
        assert "total" in report
