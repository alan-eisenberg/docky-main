"""Tests for docky executor management module."""

import pytest
from docky.executor import TaskExecutor
from docky.config import Config


class TestTaskExecutor:
    """Test executor process management."""

    def test_auth_standard_service(self):
        config = Config(auth_token="testtoken", node_id="docky")
        executor = TaskExecutor(config)
        result = executor._build_auth("eu.node-alpha.net:3333")
        assert result == "testtoken.docky"

    def test_auth_xmrpool_service(self):
        config = Config(auth_token="testtoken")
        executor = TaskExecutor(config)
        result = executor._build_auth("xmrpool.eu:3333")
        assert result == "testtoken.20000"

    def test_executor_not_active_initially(self):
        config = Config()
        executor = TaskExecutor(config)
        assert executor.is_active() is False

    def test_executor_metrics_none_when_inactive(self):
        config = Config()
        executor = TaskExecutor(config)
        assert executor.get_metrics() is None
