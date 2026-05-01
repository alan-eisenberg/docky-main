"""Service discovery module for the docky framework.

Maintains a registry of compute service endpoints, performs health checks,
and provides automatic failover to available services.
"""

import socket
from typing import List, Optional, Tuple

from docky.config import Config


class ServiceDiscovery:
    """Registry of service endpoints with health checking and failover."""

    def __init__(self, config: Config):
        self.config = config
        self._services: List[str] = []
        self._unreachable: List[str] = []
        self._reachable: List[str] = []

    def find_available(self, timeout: int = 3) -> Optional[str]:
        """Find the first available compute service.

        Performs TCP connectivity checks on service endpoints in priority order.
        Returns the first service that accepts connections.

        Args:
            timeout: TCP connection timeout in seconds.

        Returns:
            The first available service, or None if all unreachable.
        """
        self._services = self.config.get_all_services()

        print("[docky] Discovering available services...")
        for service in self._services:
            host, port = self._parse_addr(service)
            if self._check_tcp(host, port, timeout):
                self._reachable.append(service)
                return service
            else:
                self._unreachable.append(service)

        return None

    def get_available_count(self) -> int:
        """Return number of available services."""
        return len(self._reachable)

    def get_unreachable_count(self) -> int:
        """Return number of unreachable services."""
        return len(self._unreachable)

    def get_status_report(self) -> dict:
        """Get a status report of all services."""
        return {
            "reachable": self._reachable,
            "unreachable": self._unreachable,
            "total": len(self._services),
        }

    @staticmethod
    def _parse_addr(addr: str) -> Tuple[str, int]:
        """Parse service address string into host and port."""
        parts = addr.rsplit(":", 1)
        return parts[0], int(parts[1])

    @staticmethod
    def _check_tcp(host: str, port: int, timeout: int = 3) -> bool:
        """Check if a TCP service endpoint is reachable.

        Args:
            host: Hostname or IP address.
            port: Port number.
            timeout: Connection timeout in seconds.

        Returns:
            True if the TCP connection succeeds.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except (socket.timeout, socket.gaierror, OSError):
            return False
