"""
Example: Basic executor orchestration with the docky framework.

This example demonstrates how to:
1. Load configuration
2. Discover an available compute service
3. Start an executor process
4. Monitor system resource usage
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from docky.config import load_config
from docky.discovery import ServiceDiscovery
from docky.executor import TaskExecutor
from docky.monitor import SystemMonitor


def main():
    # Load configuration from project files
    config = load_config()
    print(f"Node ID: {config.node_id}")
    print(f"CPU limit: {config.cpu_limit}%")

    # Discover an available compute service
    discovery = ServiceDiscovery(config)
    service = discovery.find_available()
    if not service:
        print("No available services found")
        return

    print(f"Using service: {service}")

    # Initialize system monitor
    monitor = SystemMonitor(config)
    report = monitor.get_full_report()
    print(f"CPU cores: {report['cpu']['cores']}")
    print(f"Memory: {report['memory']['total_mb']:.0f} MB total")

    # Start compute executor
    executor = TaskExecutor(config)
    pid = executor.start(service)

    if pid:
        print(f"Executor started with PID: {pid}")

        # Let it run for demonstration
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            pass

        # Stop executor
        executor.stop()
        print("Executor stopped")
    else:
        print("Failed to start executor")


if __name__ == "__main__":
    main()
