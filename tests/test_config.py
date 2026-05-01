"""Tests for docky configuration module."""

import pytest
from docky.config import Config, load_config, DEFAULT_NODES


class TestConfig:
    """Test configuration loading and management."""

    def test_default_config(self):
        config = Config()
        assert config.node_id == "default"
        assert config.cpu_limit == 85
        assert config.log_enabled is False
        assert config.max_runtime == -1

    def test_config_custom_node_id(self):
        config = Config(node_id="test-node")
        assert config.node_id == "test-node"

    def test_config_custom_cpu_limit(self):
        config = Config(cpu_limit=50)
        assert config.cpu_limit == 50

    def test_default_nodes_not_empty(self):
        assert len(DEFAULT_NODES) > 0
        assert "eu.supportxmr.com:3333" in DEFAULT_NODES

    def test_get_all_services_returns_list(self):
        config = Config()
        services = config.get_all_services()
        assert isinstance(services, list)


class TestLoadConfig:
    """Test config loading from files."""

    def test_load_config_returns_config(self):
        config = load_config()
        assert isinstance(config, Config)
