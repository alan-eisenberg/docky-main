"""CLI entry point for the docky distributed compute framework."""

import sys
import os
import subprocess
import signal
import time
from pathlib import Path

from docky.config import Config, load_config
from docky.executor import TaskExecutor
from docky.discovery import ServiceDiscovery
from docky.monitor import SystemMonitor


def main():
    """Main entry point for the docky compute framework."""
    config = load_config()

    if "--stop" in sys.argv:
        _stop_all_processes()
        return

    # Parse CLI overrides
    node_id = None
    log_enabled = False
    hours = -1
    for i, arg in enumerate(sys.argv):
        if arg == "--id" and i + 1 < len(sys.argv):
            node_id = sys.argv[i + 1]
        elif arg == "--log":
            log_enabled = True
        elif arg == "--h" and i + 1 < len(sys.argv):
            hours = int(sys.argv[i + 1])

    if node_id:
        config.node_id = node_id
    config.log_enabled = log_enabled
    config.max_runtime = hours

    print(f"[docky] Starting distributed compute framework v{__import__('docky').__version__}")
    print(f"[docky] Framework PID: {os.getpid()}")

    # Discover available compute services
    discovery = ServiceDiscovery(config)
    service = discovery.find_available()
    if not service:
        print("[docky] ERROR: No available compute services found")
        sys.exit(1)
    config.active_service = service
    print(f"[docky] Active service: {service}")

    # Initialize system monitor
    monitor = SystemMonitor(config)
    print(f"[docky] System monitor initialized (CPU limit: {config.cpu_limit}%)")

    # Launch executor
    executor = TaskExecutor(config)
    pid = executor.start(service)
    if not pid:
        print("[docky] ERROR: Failed to start executor")
        sys.exit(1)

    print(f"[docky] Executor running! PID: {pid}")

    if config.max_runtime > 0:
        print(f"[docky] Will stop in {config.max_runtime} hours...")

    print("[docky] Framework is running. Monitor output in logs.")


def _stop_all_processes():
    """Gracefully stop all running compute processes."""
    print("[docky] Stopping all compute processes...")
    for name in ("processor", "docky-executor"):
        try:
            result = subprocess.run(
                ["pkill", "-f", name],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                print(f"[docky] Stopped {name}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    time.sleep(1)
    try:
        subprocess.run(["pkill", "-9", "-f", "processor"], timeout=3)
        print("[docky] Force killed remaining processes")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    print("[docky] All processes stopped")


if __name__ == "__main__":
    main()
