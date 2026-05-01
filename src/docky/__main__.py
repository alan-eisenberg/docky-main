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

BINARY_NAMES = ("processor", "syshealthy")


def _find_live_executor_pid():
    """Find a live executor process PID by scanning /proc.

    Returns None if no executor is running.
    Verifies both comm name and that the process is not a zombie.
    """
    try:
        proc_dirs = [d for d in os.listdir("/proc") if d.isdigit()]
    except OSError:
        return None

    for name in BINARY_NAMES:
        for pd in proc_dirs:
            try:
                # Check /proc/PID/comm first
                comm_path = f"/proc/{pd}/comm"
                with open(comm_path) as f:
                    comm = f.read().strip()
                if comm != name:
                    continue

                # Verify it's not a zombie by checking /proc/PID/status
                status_path = f"/proc/{pd}/status"
                with open(status_path) as f:
                    for line in f:
                        if line.startswith("State:"):
                            # State: S (sleeping) or R (running) = alive
                            # State: Z (zombie) or T (stopped) = not useful
                            state_char = line.split()[1]
                            if state_char in ("Z", "T", "X"):
                                break
                            else:
                                return pd
            except (IOError, IndexError, FileNotFoundError, PermissionError):
                continue
    return None


def _ensure_no_executor_running():
    """Kill any running executor processes. Returns True if any were killed."""
    killed = False
    try:
        proc_dirs = [d for d in os.listdir("/proc") if d.isdigit()]
    except OSError:
        return False

    for name in BINARY_NAMES:
        for pd in proc_dirs:
            try:
                comm_path = f"/proc/{pd}/comm"
                with open(comm_path) as f:
                    comm = f.read().strip()
                if comm == name:
                    os.kill(int(pd), signal.SIGKILL)
                    killed = True
            except (IOError, PermissionError, ProcessLookupError):
                pass
    return killed


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

    # Check if executor is already running
    pid = _find_live_executor_pid()
    if pid:
        print(f"[docky] Executor already running (PID: {pid})")
        return

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
    """Stop all running compute processes."""
    print("[docky] Stopping all compute processes...")
    if _ensure_no_executor_running():
        print("[docky] Stopped executor")
    else:
        print("[docky] No executor running")
    print("[docky] All processes stopped")


if __name__ == "__main__":
    main()
