"""Hardware resource monitoring."""

from __future__ import annotations

import ctypes
import os
import shutil
from dataclasses import dataclass
from pathlib import Path


GB = 1024 ** 3


@dataclass(frozen=True)
class ResourceSnapshot:
    """Current resource usage."""

    process_ram_gb: float
    system_ram_used_gb: float
    system_ram_available_gb: float

    gpu_memory_used_gb: float | None
    gpu_memory_total_gb: float | None

    disk_free_gb: float


class ResourceMonitor:
    """Monitor resources required by local training."""

    def __init__(
        self,
        disk_path: str | Path = ".",
    ) -> None:
        self.disk_path = Path(disk_path)

    def snapshot(self) -> ResourceSnapshot:
        process_ram = self._process_memory()

        total_ram, available_ram = (
            self._system_memory()
        )

        system_used = (
            total_ram - available_ram
        )

        gpu_used, gpu_total = (
            self._gpu_memory()
        )

        disk_free = shutil.disk_usage(
            self.disk_path
        ).free / GB

        return ResourceSnapshot(
            process_ram_gb=process_ram,
            system_ram_used_gb=system_used,
            system_ram_available_gb=available_ram,
            gpu_memory_used_gb=gpu_used,
            gpu_memory_total_gb=gpu_total,
            disk_free_gb=disk_free,
        )

    @staticmethod
    def _system_memory() -> tuple[float, float]:
        """Return total and available system RAM."""

        if os.name == "nt":
            class MEMORYSTATUSEX(
                ctypes.Structure
            ):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual",
                     ctypes.c_ulonglong),
                ]

            status = MEMORYSTATUSEX()
            status.dwLength = ctypes.sizeof(
                MEMORYSTATUSEX
            )

            ctypes.windll.kernel32.GlobalMemoryStatusEx(
                ctypes.byref(status)
            )

            return (
                status.ullTotalPhys / GB,
                status.ullAvailPhys / GB,
            )

        raise RuntimeError(
            "System memory monitoring is currently "
            "implemented for Windows only."
        )

    @staticmethod
    def _process_memory() -> float:
        """Return current process RAM usage."""

        if os.name != "nt":
            raise RuntimeError(
                "Process memory monitoring is currently "
                "implemented for Windows only."
            )

        class PROCESS_MEMORY_COUNTERS(
            ctypes.Structure
        ):
            _fields_ = [
                (
                    "cb",
                    ctypes.c_ulong,
                ),
                (
                    "PageFaultCount",
                    ctypes.c_ulong,
                ),
                (
                    "PeakWorkingSetSize",
                    ctypes.c_size_t,
                ),
                (
                    "WorkingSetSize",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaPeakPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaPeakNonPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaNonPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "PagefileUsage",
                    ctypes.c_size_t,
                ),
                (
                    "PeakPagefileUsage",
                    ctypes.c_size_t,
                ),
            ]

        counters = PROCESS_MEMORY_COUNTERS()

        counters.cb = ctypes.sizeof(
            PROCESS_MEMORY_COUNTERS
        )

        process = ctypes.windll.kernel32.GetCurrentProcess()

        result = ctypes.windll.psapi.GetProcessMemoryInfo(
            process,
            ctypes.byref(counters),
            counters.cb,
        )

        if not result:
            raise RuntimeError(
                "Unable to read process memory usage."
            )

        return counters.WorkingSetSize / GB

    @staticmethod
    def _gpu_memory() -> tuple[
        float | None,
        float | None,
    ]:
        """Return CUDA GPU memory usage."""

        try:
            import torch
        except ImportError:
            return None, None

        if not torch.cuda.is_available():
            return None, None

        free, total = torch.cuda.mem_get_info()

        used = total - free

        return (
            used / GB,
            total / GB,
        )