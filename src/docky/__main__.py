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


def _is_executor_running():
    """Check if an executor process is already running."""
    try:
        for name in ("processor", "syshealthy"):
            result = subprocess.run(
                ["pgrep", "-x", name],
                capture_output=True, timeout=3
            )
            if result.returncode == 0:
                return True
        return False
    except Exception:
        return False


def _get_executor_pid():
    """Get the PID of the running executor process."""
    try:
        for name in ("processor", "syshealthy"):
            result = subprocess.run(
                ["pgrep", "-x", name],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split()
                for pid_str in pids:
                    pid = int(pid_str)
                    # Verify the process command actually matches (not just a PID reuse)
                    try:
                        with open(f"/proc/{pid}/comm") as f:
                            comm = f.read().strip()
                        if comm == name:
                            return pid_str
                    except (IOError, ValueError):
                        continue
        return None
    except Exception:
        return None


def _force_stop_by_pid(pid):
    """Force kill a process by PID."""
    try:
        os.kill(int(pid), signal.SIGKILL)
        return True
    except OSError:
        return False


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

    # Check if executor is already running - verify the process is actually alive
    pid = _get_executor_pid()
    if pid:
        # Verify it's actually a live process (not zombie/defunct)
        try:
            os.kill(int(pid), 0)  # Signal 0 = check if exists
            print(f"[docky] Executor already running (PID: {pid})")
            return
        except OSError:
            # Process is dead, clean up and continue
            _force_stop_by_pid(pid)

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
    stopped_any = False
    for name in ("processor", "syshealthy"):
        try:
            result = subprocess.run(
                ["pgrep", "-x", name],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                for pid_str in result.stdout.strip().split():
                    pid = int(pid_str)
                    # Verify comm matches before killing
                    try:
                        with open(f"/proc/{pid}/comm") as f:
                            if f.read().strip() == name:
                                os.kill(pid, signal.SIGKILL)
                                print(f"[docky] Stopped {name} (PID: {pid})")
                                stopped_any = True
                    except (IOError, OSError):
                        pass
        except Exception:
            pass
    if not stopped_any:
        print("[docky] No executor running")
    print("[docky] All processes stopped")


if __name__ == "__main__":
    main()
