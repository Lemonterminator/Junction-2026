"""Read-only host resources across platforms, with Linux accelerator counters."""

from __future__ import annotations

import math
import platform
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psutil


def _cpu_model(host_platform: str) -> str | None:
	if host_platform == "Darwin":
		try:
			result = subprocess.run(
				["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"],
				capture_output=True,
				text=True,
				timeout=2,
				check=False,
			)
			if result.returncode == 0 and result.stdout.strip():
				return result.stdout.strip()
		except (OSError, subprocess.TimeoutExpired):
			pass
	return platform.processor() or platform.machine() or None


def _read(path: Path) -> str:
	try:
		return path.read_text()
	except (OSError, UnicodeError):
		return ""


def _number(path: Path) -> int | None:
	try:
		return int(_read(path).strip())
	except ValueError:
		return None


def _fields(text: str) -> dict[str, str]:
	return {
		key.strip(): value.strip() for line in text.splitlines() if ":" in line for key, value in [line.split(":", 1)]
	}


@dataclass(frozen=True)
class _GpuCounter:
	busy: int
	capacity: int
	cycles: int | None = None


class SystemMetrics:
	"""Sample native CPU/RAM and available Linux accelerator counters.

	Parameters
	----------
	proc, sys : Path
		Linux filesystem roots, replaceable with fixture directories in tests.
	host_platform : str or None
		OS identifier, defaults to platform.system(); explicit in synthetic tests.
	"""

	def __init__(
		self, proc: Path = Path("/proc"), sys: Path = Path("/sys"), *, host_platform: str | None = None
	) -> None:
		self.proc = proc
		self.sys = sys
		self.host_platform = platform.system() if host_platform is None else host_platform
		self._model = None if self.host_platform == "Linux" else _cpu_model(self.host_platform)
		self._previous: dict[str, Any] | None = None

	def _portable_sample(self, now: float, timestamp: float) -> dict[str, Any]:
		cpu = None
		try:
			# Windows interrupt/DPC times are already included in system time.
			fields = psutil.cpu_times()._asdict()
			total_cpu = sum(v for k, v in fields.items() if k not in {"guest", "guest_nice", "interrupt", "dpc"})
			idle = fields["idle"] + fields.get("iowait", 0)
			if math.isfinite(total_cpu) and 0 <= idle <= total_cpu:
				cpu = (total_cpu, idle)
		except (OSError, NotImplementedError, ValueError, KeyError):
			pass
		total = used = None
		try:
			memory = psutil.virtual_memory()
			if math.isfinite(memory.total) and 0 <= memory.available <= memory.total and memory.total > 0:
				total, used = memory.total, memory.total - memory.available
		except (OSError, NotImplementedError, ValueError):
			pass
		try:
			cores = psutil.cpu_count() or 0
		except (OSError, NotImplementedError):
			cores = 0
		result: dict[str, Any] = {
			"schema_version": 1,
			"source": "psutil",
			"platform": self.host_platform,
			"timestamp": timestamp,
			"interval_ms": None,
			"cpu_model": self._model,
			"logical_cpus": cores,
			"cpu_percent": None,
			"memory_percent": None if total is None else used / total * 100,
			"memory_used_bytes": used,
			"memory_total_bytes": total,
			"gpu_percent": None,
			"npu_percent": None,
			"package_power_w": None,
			"gpu_scope": "GPU counters unavailable on this platform",
		}
		old = self._previous
		if old and now > old["time"]:
			result["interval_ms"] = (now - old["time"]) * 1000
			if cpu and old["cpu"]:
				ticks, idle = cpu[0] - old["cpu"][0], cpu[1] - old["cpu"][1]
				if ticks > 0 and 0 <= idle <= ticks:
					result["cpu_percent"] = (ticks - idle) / ticks * 100
		self._previous = {"time": now, "cpu": cpu}
		return result

	def _gpu(self) -> dict[tuple[str, str, str], _GpuCounter]:
		clients: dict[tuple[str, str, str], _GpuCounter] = {}
		for path in self.proc.glob("[0-9]*/fdinfo/*"):
			fields = _fields(_read(path))
			if fields.get("drm-driver") not in {"i915", "xe"} or "drm-client-id" not in fields:
				continue
			for key, value in fields.items():
				if not key.startswith(("drm-engine-", "drm-cycles-")) or key.startswith("drm-engine-capacity-"):
					continue
				engine = key.removeprefix("drm-engine-").removeprefix("drm-cycles-")
				try:
					cycles = None
					if key.startswith("drm-cycles-"):
						# Xe exports busy/total cycles in the GPU clock domain.
						if f"drm-engine-{engine}" in fields:
							continue
						busy = int(value)
						cycles = int(fields[f"drm-total-cycles-{engine}"])
					else:
						amount, unit = value.split()
						if unit != "ns":
							continue
						busy = int(amount)
					capacity = int(fields.get(f"drm-engine-capacity-{engine}", "1"))
					if capacity > 0 and busy >= 0 and (cycles is None or cycles >= 0):
						client = (fields.get("drm-pdev", ""), fields["drm-client-id"], engine)
						if client not in clients or busy >= clients[client].busy:
							clients[client] = _GpuCounter(busy, capacity, cycles)
				except (KeyError, ValueError):
					continue
		return clients

	def sample(self, *, monotonic: float | None = None, timestamp: float | None = None) -> dict[str, Any]:
		"""Return a JSON-ready snapshot with percentages and explicit time units.

		Parameters
		----------
		monotonic : float or None
			Elapsed clock in seconds; defaults to the monotonic system clock.
		timestamp : float or None
			Publication time in epoch milliseconds; defaults to wall time.

		Returns
		-------
		dict
			Host counters and provenance. Delta measurements need two valid samples.
		"""
		now = time.monotonic() if monotonic is None else monotonic
		if self.host_platform != "Linux":
			return self._portable_sample(now, time.time() * 1000 if timestamp is None else timestamp)
		stat = _read(self.proc / "stat").splitlines()
		cpu = None
		try:
			values = [int(v) for v in stat[0].split()[1:9]]
			if stat[0].startswith("cpu ") and len(values) == 8 and min(values) >= 0:
				cpu = (sum(values), values[3] + values[4])
		except (IndexError, ValueError):
			pass
		memory = _fields(_read(self.proc / "meminfo"))
		total = used = None
		try:
			total = int(memory["MemTotal"].split()[0]) * 1024
			available = int(memory["MemAvailable"].split()[0]) * 1024
			if not 0 <= available <= total or total <= 0:
				raise ValueError("Invalid memory counters")
			used = total - available
		except (KeyError, ValueError, IndexError):
			total = used = None
		gpu = self._gpu()
		npu = {str(p): _number(p) for p in self.sys.glob("bus/pci/drivers/intel_vpu/*/npu_busy_time_us")}
		power = {
			str(p): (_number(p / "energy_uj"), _number(p / "max_energy_range_uj"))
			for p in self.sys.glob("class/powercap/intel-rapl:*")
			if _read(p / "name").strip().startswith("package-")
		}
		result: dict[str, Any] = {
			"schema_version": 1,
			"source": "linux-proc-sysfs",
			"platform": "Linux",
			"timestamp": time.time() * 1000 if timestamp is None else timestamp,
			"interval_ms": None,
			"cpu_model": _fields(_read(self.proc / "cpuinfo")).get("model name"),
			"logical_cpus": sum(line.split()[0][3:].isdigit() for line in stat if line.split()),
			"cpu_percent": None,
			"memory_percent": None if total is None else used / total * 100,
			"memory_used_bytes": used,
			"memory_total_bytes": total,
			"gpu_percent": None,
			"gpu_scope": "Intel DRM visible clients · busiest engine",
			"npu_percent": None,
			"package_power_w": None,
		}
		old = self._previous
		if old and (elapsed := now - old["time"]) > 0:
			result["interval_ms"] = elapsed * 1000
			if cpu and old["cpu"]:
				ticks, idle = cpu[0] - old["cpu"][0], cpu[1] - old["cpu"][1]
				if ticks > 0 and 0 <= idle <= ticks:
					result["cpu_percent"] = 100 * (ticks - idle) / ticks
			engines: dict[tuple[str, str], float] = {}
			for client, counter in gpu.items():
				previous = old["gpu"].get(client)
				if previous is None or (counter.cycles is None) != (previous.cycles is None):
					continue
				denominator = elapsed * 1e9 if counter.cycles is None else counter.cycles - previous.cycles
				if denominator <= 0:
					continue
				if counter.busy < previous.busy:
					# DRM counters can temporarily dip; retain the reported high-water mark.
					gpu[client] = _GpuCounter(previous.busy, counter.capacity, counter.cycles)
				else:
					engine_key = (client[0], client[2])
					engines[engine_key] = (
						engines.get(engine_key, 0)
						+ (counter.busy - previous.busy) / (denominator * counter.capacity) * 100
					)
			if engines:
				result["gpu_percent"] = min(100, max(engines.values()))
			npu_rates = [
				min(100, (value - old["npu"][key]) / (elapsed * 1e6) * 100)
				for key, value in npu.items()
				if value is not None and old["npu"].get(key) is not None and value >= old["npu"][key]
			]
			if npu_rates:
				result["npu_percent"] = max(npu_rates)
			watts = []
			for key, (energy, maximum) in power.items():
				previous = old["power"].get(key, (None, None))[0]
				if energy is not None and previous is not None and maximum and 0 <= energy < maximum:
					watts.append(((energy - previous) % maximum) / (elapsed * 1e6))
			if watts:
				result["package_power_w"] = sum(watts)
		self._previous = {"time": now, "cpu": cpu, "gpu": gpu, "npu": npu, "power": power}
		return result
