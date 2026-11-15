from collections import namedtuple
from pathlib import Path

import pytest

from defect_sorter import system_metrics
from defect_sorter.system_metrics import SystemMetrics


@pytest.fixture(autouse=True)
def linux_fixture_platform(monkeypatch):
	monkeypatch.setattr(system_metrics.platform, "system", lambda: "Linux")


def write(root: Path, name: str, value: str) -> None:
	path = root / name
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(value)


@pytest.fixture
def roots(tmp_path):
	proc, sys = tmp_path / "proc", tmp_path / "sys"
	write(proc, "stat", "cpu 10 0 10 80 0 0 0 0 5 0\ncpu0 0\ncpu1 0\n")
	write(proc, "meminfo", "MemTotal: 1000 kB\nMemAvailable: 750 kB\n")
	write(proc, "cpuinfo", "model name : Test Intel CPU\n")
	return proc, sys


def test_cpu_deltas_exclude_guest_time_and_memory_uses_available(roots):
	proc, sys = roots
	metrics = SystemMetrics(proc, sys)
	first = metrics.sample(monotonic=10, timestamp=1000)
	assert first["cpu_percent"] is None
	assert first["memory_percent"] == 25
	assert first["memory_used_bytes"] == 250 * 1024
	write(proc, "stat", "cpu 30 0 20 150 0 0 0 0 20 0\ncpu0 0\ncpu1 0\n")
	second = metrics.sample(monotonic=11, timestamp=2000)
	assert second["cpu_percent"] == 30
	assert second["cpu_model"] == "Test Intel CPU"
	assert second["logical_cpus"] == 2
	assert second["timestamp"] == 2000
	assert second["interval_ms"] == 1000


def fdinfo(busy: int, client: int = 1) -> str:
	return (
		f"drm-driver: xe\ndrm-pdev: 0000:00:02.0\ndrm-client-id: {client}\n"
		f"drm-engine-compute: {busy} ns\ndrm-engine-capacity-compute: 2\n"
	)


def test_gpu_deduplicates_clients_and_normalizes_engine_capacity(roots):
	proc, sys = roots
	write(proc, "123/fdinfo/3", fdinfo(100_000_000))
	write(proc, "123/fdinfo/4", fdinfo(100_000_000))
	metrics = SystemMetrics(proc, sys)
	metrics.sample(monotonic=10, timestamp=1000)
	write(proc, "123/fdinfo/3", fdinfo(1_100_000_000))
	write(proc, "123/fdinfo/4", fdinfo(1_100_000_000))
	second = metrics.sample(monotonic=11, timestamp=2000)
	assert second["gpu_percent"] == 50
	assert "visible clients" in second["gpu_scope"]


def test_gpu_counter_dips_hold_the_high_water_mark_until_caught_up(roots):
	proc, sys = roots
	write(proc, "123/fdinfo/3", fdinfo(2_000_000_000))
	metrics = SystemMetrics(proc, sys)
	metrics.sample(monotonic=10, timestamp=1000)
	write(proc, "123/fdinfo/3", fdinfo(1_000_000_000))
	assert metrics.sample(monotonic=11, timestamp=2000)["gpu_percent"] is None
	write(proc, "123/fdinfo/3", fdinfo(1_500_000_000))
	assert metrics.sample(monotonic=12, timestamp=3000)["gpu_percent"] is None
	write(proc, "123/fdinfo/3", fdinfo(2_200_000_000))
	assert metrics.sample(monotonic=13, timestamp=4000)["gpu_percent"] == 10


def test_xe_cycle_counters_use_gpu_clock_and_capacity_without_double_counting(roots):
	proc, sys = roots

	def cycles(busy: int, total: int, client: int = 1) -> str:
		return (
			f"drm-driver: xe\ndrm-pdev: 0000:00:02.0\ndrm-client-id: {client}\n"
			f"drm-cycles-ccs: {busy}\ndrm-total-cycles-ccs: {total}\ndrm-engine-capacity-ccs: 4\n"
		)

	write(proc, "123/fdinfo/3", cycles(1000, 2000))
	write(proc, "123/fdinfo/4", cycles(1000, 2000))
	write(proc, "456/fdinfo/3", cycles(1000, 2000, 2))
	metrics = SystemMetrics(proc, sys)
	metrics.sample(monotonic=10, timestamp=1000)
	write(proc, "123/fdinfo/3", cycles(3000, 3000))
	write(proc, "123/fdinfo/4", cycles(3000, 3000))
	write(proc, "456/fdinfo/3", cycles(2000, 3000, 2))
	assert metrics.sample(monotonic=12, timestamp=3000)["gpu_percent"] == 75
	write(proc, "123/fdinfo/3", cycles(3000, 3000))
	write(proc, "123/fdinfo/4", cycles(3000, 3000))
	write(proc, "456/fdinfo/3", cycles(2000, 3000, 2))
	assert metrics.sample(monotonic=13, timestamp=4000)["gpu_percent"] is None


def test_new_or_reset_accelerator_counters_do_not_invent_utilization(roots):
	proc, sys = roots
	metrics = SystemMetrics(proc, sys)
	metrics.sample(monotonic=10, timestamp=1000)
	write(proc, "123/fdinfo/3", fdinfo(2_000_000_000))
	npu = "bus/pci/drivers/intel_vpu/0000:00:0b.0/npu_busy_time_us"
	write(sys, npu, "900000")
	assert metrics.sample(monotonic=11, timestamp=2000)["gpu_percent"] is None
	write(proc, "123/fdinfo/3", fdinfo(1))
	write(sys, npu, "100000")
	sample = metrics.sample(monotonic=12, timestamp=3000)
	assert sample["gpu_percent"] is None
	assert sample["npu_percent"] is None


def test_npu_and_package_power_use_elapsed_time_and_energy_wrap(roots):
	proc, sys = roots
	npu = "bus/pci/drivers/intel_vpu/0000:00:0b.0/npu_busy_time_us"
	power = "class/powercap/intel-rapl:0"
	write(sys, npu, "1000000")
	write(sys, f"{power}/name", "package-0")
	write(sys, f"{power}/energy_uj", "9000000")
	write(sys, f"{power}/max_energy_range_uj", "10000000")
	metrics = SystemMetrics(proc, sys)
	metrics.sample(monotonic=10, timestamp=1000)
	write(sys, npu, "1500000")
	write(sys, f"{power}/energy_uj", "3000000")
	sample = metrics.sample(monotonic=12, timestamp=3000)
	assert sample["npu_percent"] == 25
	assert sample["package_power_w"] == 2


def test_missing_malformed_and_non_linux_counters_remain_null(tmp_path):
	proc, sys = tmp_path / "missing", tmp_path / "sys"
	metrics = SystemMetrics(proc, sys)
	sample = metrics.sample(monotonic=10, timestamp=1000)
	for key in ["cpu_percent", "memory_percent", "gpu_percent", "npu_percent", "package_power_w"]:
		assert sample[key] is None
	write(proc, "stat", "cpu broken")
	write(proc, "meminfo", "MemTotal: 10 kB\nMemAvailable: 11 kB\n")
	assert metrics.sample(monotonic=11, timestamp=2000)["memory_percent"] is None


@pytest.mark.parametrize("host_platform", ["Darwin", "Windows"])
def test_portable_cpu_memory_and_platform_use_native_counters(monkeypatch, host_platform):
	CpuTimes = namedtuple("CpuTimes", "user system idle interrupt dpc")
	Memory = namedtuple("Memory", "total available")
	times = iter([CpuTimes(10, 10, 80, 3, 2), CpuTimes(30, 20, 150, 9, 6)])
	monkeypatch.setattr(system_metrics.psutil, "cpu_times", lambda: next(times))
	monkeypatch.setattr(system_metrics.psutil, "cpu_count", lambda: 8)
	monkeypatch.setattr(system_metrics.psutil, "virtual_memory", lambda: Memory(4096, 3072))
	monkeypatch.setattr(system_metrics, "_cpu_model", lambda _: "Test native CPU")
	metrics = SystemMetrics(host_platform=host_platform)
	first = metrics.sample(monotonic=10, timestamp=1000)
	assert first["cpu_percent"] is None
	assert first["memory_used_bytes"] == 1024
	assert first["memory_percent"] == 25
	second = metrics.sample(monotonic=11, timestamp=2000)
	assert second["cpu_percent"] == 30
	assert second["source"] == "psutil"
	assert second["platform"] == host_platform
	assert second["cpu_model"] == "Test native CPU"
	assert second["logical_cpus"] == 8
	assert second["gpu_percent"] is None
	assert second["npu_percent"] is None


def test_portable_counter_failures_do_not_erase_available_memory(monkeypatch):
	def unavailable():
		raise OSError("Counter unavailable")

	Memory = namedtuple("Memory", "total available")
	monkeypatch.setattr(system_metrics.psutil, "cpu_times", unavailable)
	monkeypatch.setattr(system_metrics.psutil, "cpu_count", lambda: None)
	monkeypatch.setattr(system_metrics.psutil, "virtual_memory", lambda: Memory(4096, 1024))
	monkeypatch.setattr(system_metrics, "_cpu_model", lambda _: "Test CPU")
	sample = SystemMetrics(host_platform="Darwin").sample(monotonic=10, timestamp=1000)
	assert sample["cpu_percent"] is None
	assert sample["logical_cpus"] == 0
	assert sample["memory_percent"] == 75


def proc_stat(pid: int, comm: str, utime: int, stime: int, rss_pages: int) -> str:
	# Fields after the command: state ppid pgrp session tty tpgid flags minflt cminflt majflt cmajflt utime stime
	# cutime cstime priority nice threads itrealvalue starttime vsize rss.
	rest = ["S", "1", "1", "1", "0", "-1", "0", "0", "0", "0", "0", str(utime), str(stime)]
	rest += ["0", "0", "20", "0", "1", "0", "100", "1000", str(rss_pages)]
	return f"{pid} ({comm}) " + " ".join(rest) + "\n"


def test_per_core_cpu_and_top_processes_come_from_procfs_deltas(roots):
	proc, sys = roots
	write(proc, "stat", "cpu 0 0 0 0 0 0 0 0\ncpu0 0 0 0 100 0 0 0 0\ncpu1 0 0 0 100 0 0 0 0\n")
	write(proc, "100/stat", proc_stat(100, "python3", 10, 0, 2560))
	write(proc, "200/stat", proc_stat(200, "Web Content", 0, 0, 256))
	write(proc, "300/stat", proc_stat(300, "idle thing", 5, 5, 1))
	metrics = SystemMetrics(proc, sys, clock_ticks=100, page_size=4096)
	first = metrics.sample(monotonic=10, timestamp=1000)
	assert first["per_cpu_percent"] is None
	assert first["processes"] is None
	write(proc, "stat", "cpu 0 0 0 0 0 0 0 0\ncpu0 75 0 25 200 0 0 0 0\ncpu1 10 0 0 290 0 0 0 0\n")
	# Over 2 s at 100 ticks/s: python3 used 150 ticks (75 %), Web Content 20 ticks (10 %), the idle one nothing.
	write(proc, "100/stat", proc_stat(100, "python3", 110, 50, 2560))
	write(proc, "200/stat", proc_stat(200, "Web Content", 20, 0, 256))
	write(proc, "300/stat", proc_stat(300, "idle thing", 5, 5, 1))
	write(proc, "400/stat", proc_stat(400, "new", 999, 0, 1))
	second = metrics.sample(monotonic=12, timestamp=3000)
	assert second["per_cpu_percent"] == [50, 5]
	assert second["processes"] == [
		{"pid": 100, "name": "python3", "cpu_percent": 75, "memory_bytes": 2560 * 4096},
		{"pid": 200, "name": "Web Content", "cpu_percent": 10, "memory_bytes": 256 * 4096},
		{"pid": 300, "name": "idle thing", "cpu_percent": 0, "memory_bytes": 4096},
	], "a process first seen in this sample has no rate yet and is left out"


def test_unreadable_process_entries_are_skipped(roots):
	proc, sys = roots
	write(proc, "100/stat", "garbage")
	write(proc, "200/stat", proc_stat(200, "ok", 0, 0, 1))
	metrics = SystemMetrics(proc, sys, clock_ticks=100, page_size=4096)
	metrics.sample(monotonic=1, timestamp=1)
	assert [p["pid"] for p in metrics.sample(monotonic=2, timestamp=2)["processes"]] == [200]
