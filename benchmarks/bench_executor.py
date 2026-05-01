"""
Benchmark: Executor startup performance.

Measures the time required to initialize a compute executor and establish
a connection to a compute service.
"""

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from docky.config import Config, load_config
from docky.discovery import ServiceDiscovery
from docky.executor import TaskExecutor


def benchmark_service_discovery():
    """Benchmark service discovery time."""
    config = load_config()
    discovery = ServiceDiscovery(config)

    start = time.time()
    service = discovery.find_available(timeout=2)
    elapsed = time.time() - start

    print(f"Service discovery: {elapsed:.2f}s")
    print(f"  Available: {discovery.get_available_count()}")
    print(f"  Unreachable: {discovery.get_unreachable_count()}")
    if service:
        print(f"  Selected: {service}")
    return elapsed


def benchmark_system_monitor():
    """Benchmark system monitoring overhead."""
    config = load_config()
    from docky.monitor import SystemMonitor
    monitor = SystemMonitor(config)

    iterations = 100
    start = time.time()
    for _ in range(iterations):
        monitor.get_full_report()
    elapsed = time.time() - start

    print(f"System report ({iterations} iterations): {elapsed:.3f}s")
    print(f"  Per-call: {elapsed/iterations*1000:.3f}ms")
    return elapsed


if __name__ == "__main__":
    print("=== Docky Benchmark Suite ===\n")

    print("--- Service Discovery ---")
    benchmark_service_discovery()

    print("\n--- System Monitoring ---")
    benchmark_system_monitor()

    print("\nDone.")
