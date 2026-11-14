import pytest
from armkit.guard import ContactGuard, ContactKind, GuardLimits

DT = 0.05


def feed(guard, samples, *, start_t=0.0):
	"""Feed (position, load, pushing) samples at 20 Hz; return the first contact and its sample index."""
	for i, (pos, load, pushing) in enumerate(samples):
		contact = guard.update(start_t + i * DT, pos, load, pushing)
		if contact is not None:
			return contact, i
	return None, None


def moving(n, load, *, speed_ticks=3.0, start=1000.0, direction=1):
	return [(start + direction * speed_ticks * i, load, True) for i in range(n)]


class TestRapidRise:
	def test_free_motion_never_triggers(self):
		contact, _ = feed(ContactGuard(GuardLimits(), 1), moving(100, 60))
		assert contact is None

	def test_a_steady_gravity_load_is_not_a_contact(self):
		contact, _ = feed(ContactGuard(GuardLimits(), 1), moving(100, 260))
		assert contact is None

	def test_a_slow_ramp_is_not_a_rapid_rise(self):
		ramp = [(1000.0 + 3 * i, 100 + 2 * i, True) for i in range(120)]  # +40 permille per second, reaching 338
		contact, _ = feed(ContactGuard(GuardLimits(), 1), ramp)
		assert contact is None

	def test_a_sudden_jump_triggers_within_the_window(self):
		samples = moving(20, 60) + [(1060.0 + 3 * i, 260, True) for i in range(10)]
		contact, i = feed(ContactGuard(GuardLimits(), 1), samples)
		assert contact.kind is ContactKind.RISE
		assert i == 20  # the first high sample
		assert contact.load == 260

	def test_the_rise_only_counts_once_the_load_itself_is_meaningful(self):
		# 10 -> 100 is a jump of 90 (above the 80 limit) but the load stays under the 120 floor
		samples = moving(20, 10) + [(1060.0 + 3 * i, 100, True) for i in range(10)]
		contact, _ = feed(ContactGuard(GuardLimits(rise_permille=80, min_load_permille=120), 1), samples)
		assert contact is None

	def test_the_sign_of_the_load_does_not_matter(self):
		samples = moving(20, -60) + [(1060.0 + 3 * i, -260, True) for i in range(10)]
		contact, _ = feed(ContactGuard(GuardLimits(), 1), samples)
		assert contact.kind is ContactKind.RISE


class TestHardLoad:
	def test_a_load_above_the_ceiling_triggers_at_once(self):
		contact, i = feed(ContactGuard(GuardLimits(), 1), [(1000.0, 450, True)])
		assert contact.kind is ContactKind.HIGH
		assert i == 0


class TestStall:
	def test_no_progress_while_pushing_triggers_after_the_window(self):
		limits = GuardLimits(stall_window_s=0.3)
		samples = moving(10, 90) + [(1027.0, 90, True)] * 20
		contact, i = feed(ContactGuard(limits, 1), samples)
		assert contact.kind is ContactKind.STALL
		assert 15 <= i <= 17  # first stalled sample is index 10; 0.3 s later is 6 samples on

	def test_slow_but_real_progress_is_not_a_stall(self):
		samples = [(1000.0 + 1.0 * i, 90, True) for i in range(60)]  # 20 ticks per second against a 2-tick limit
		contact, _ = feed(ContactGuard(GuardLimits(), 1), samples)
		assert contact is None

	def test_standing_still_without_being_commanded_is_not_a_stall(self):
		contact, _ = feed(ContactGuard(GuardLimits(), 1), [(1000.0, 90, False)] * 40)
		assert contact is None

	def test_a_stall_needs_some_load_behind_it(self):
		contact, _ = feed(ContactGuard(GuardLimits(stall_min_load_permille=80), 1), [(1000.0, 20, True)] * 40)
		assert contact is None

	def test_progress_is_measured_along_the_direction_of_travel(self):
		samples = moving(10, 90, direction=-1, start=2000.0) + [(1973.0, 90, True)] * 20
		contact, _ = feed(ContactGuard(GuardLimits(), -1), samples)
		assert contact.kind is ContactKind.STALL
		assert contact.position == pytest.approx(1973.0)
