"""System resource monitoring module for the docky framework.

Tracks CPU, memory, and system utilization of executor processes
and provides real-time metrics for capacity planning.
"""

import os
from typing import Dict


class SystemMonitor:
    """Monitors system resource utilization for compute workloads."""

    def __init__(self, config):
        self.config = config
        self.cpu_limit = config.cpu_limit

    def get_cpu_info(self) -> Dict:
        """Get CPU information and utilization."""
        try:
            with open("/proc/cpuinfo") as f:
                content = f.read()
            cpu_count = content.count("processor")
            model = ""
            for line in content.split("\n"):
                if "model name" in line:
                    model = line.split(":", 1)[1].strip()
                    break
            return {
                "cores": cpu_count,
                "model": model,
                "limit_percent": self.cpu_limit,
            }
        except (FileNotFoundError, IndexError):
            return {"cores": os.cpu_count() or 1, "model": "unknown"}

    def get_memory_info(self) -> Dict:
        """Get memory information."""
        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            meminfo = {}
            for line in lines[:10]:
                parts = line.split()
                meminfo[parts[0].rstrip(":")] = int(parts[1])

            total_mb = meminfo.get("MemTotal", 0) / 1024
            free_mb = meminfo.get("MemFree", 0) / 1024
            avail_mb = meminfo.get("MemAvailable", free_mb) / 1024

            return {
                "total_mb": total_mb,
                "available_mb": avail_mb,
                "used_mb": total_mb - avail_mb,
                "usage_percent": ((total_mb - avail_mb) / total_mb * 100) if total_mb else 0,
            }
        except (FileNotFoundError, IndexError, ZeroDivisionError):
            return {"total_mb": 0, "available_mb": 0}

    def get_hugepages_status(self) -> Dict:
        """Check hugepages availability for optimized memory allocation."""
        try:
            with open("/proc/meminfo") as f:
                content = f.read()
            hp_total = 0
            hp_free = 0
            for line in content.split("\n"):
                if "HugePages_Total" in line:
                    hp_total = int(line.split(":")[1].strip())
                elif "HugePages_Free" in line:
                    hp_free = int(line.split(":")[1].strip())
            return {
                "total": hp_total,
                "free": hp_free,
                "supported": hp_total > 0,
            }
        except Exception:
            return {"total": 0, "free": 0, "supported": False}

    def get_full_report(self) -> Dict:
        """Generate a comprehensive resource report."""
        return {
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "hugepages": self.get_hugepages_status(),
        }
