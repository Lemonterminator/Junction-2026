import sys
import types

import pytest

COMM_SUCCESS, COMM_RX_TIMEOUT = 0, -6


class FakeSync:
	"""GroupSyncRead stand-in: fails the first ``failures`` reads, then reports fixed positions."""

	failures = 0

	def __init__(self, port, packet, address, length):
		self.calls = 0

	def addParam(self, servo_id):  # noqa: N802 - SDK name
		return True

	def txRxPacket(self):  # noqa: N802 - SDK name
		self.calls += 1
		return COMM_RX_TIMEOUT if self.calls <= FakeSync.failures else COMM_SUCCESS

	def getData(self, servo_id, address, length):  # noqa: N802 - SDK name
		return 2000 + servo_id


class FakePort:
	def __init__(self, name):
		pass

	def openPort(self):  # noqa: N802 - SDK name
		return True

	def setBaudRate(self, baud):  # noqa: N802 - SDK name
		return True

	def closePort(self):  # noqa: N802 - SDK name
		pass


class FakePacket:
	def __init__(self, protocol):
		pass

	def getTxRxResult(self, result):  # noqa: N802 - SDK name
		return "[TxRxResult] There is no status packet!"


@pytest.fixture
def reader(monkeypatch):
	sdk = types.SimpleNamespace(
		PortHandler=FakePort,
		PacketHandler=FakePacket,
		GroupSyncRead=FakeSync,
		COMM_SUCCESS=COMM_SUCCESS,
	)
	monkeypatch.setitem(sys.modules, "scservo_sdk", sdk)
	from defect_sorter.so101_reader import SO101Reader

	def make(failures: int) -> SO101Reader:
		FakeSync.failures = failures
		return SO101Reader("/dev/fake")

	return make


class TestReadTicks:
	def test_a_lost_status_packet_is_read_again(self, reader):
		arm = reader(failures=1)

		ticks = arm.read_ticks()

		assert ticks["shoulder_pan"] == 2001
		assert ticks["gripper"] == 2006

	def test_a_bus_that_keeps_failing_still_raises(self, reader):
		arm = reader(failures=10)

		with pytest.raises(OSError, match="sync read failed"):
			arm.read_ticks()
