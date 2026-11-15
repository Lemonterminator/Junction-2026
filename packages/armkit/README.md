# armkit

Kinematics, collision checking and **guarded automatic calibration** for hobby robot arms built on serial-bus
servos (Feetech STS/SCS, e.g. the SO-101). Depends on `numpy` and `scipy` only; the servo SDK is an optional extra.

## What it does

| Module | Purpose |
| --- | --- |
| `model` | Revolute-chain model: forward kinematics, numerical inverse kinematics, URDF loader. |
| `collision` | Bounding-sphere self-collision and floor checks, fitted from a URDF's STL meshes. |
| `poses` | Sweep checks, parking poses for the *other* joints, staged sweeps, collision-free transitions. |
| `guard` | Contact detection from servo load: rapid rise, hard ceiling, stall. |
| `endstop` | Creep a joint into a travel end with a leashed goal, step back on contact, confirm the end. |
| `motion` | Guarded playback of multi-joint paths with the same step-back behaviour. |
| `procedure` | `plan_calibration` (dry run) and `run_calibration` (executes on a servo bus). |
| `feetech`, `simulation` | Real Feetech bus (the only module importing the SDK) and a physics-stepped simulated bus. |
| `calibration` | Homing offsets and ranges in the LeRobot / Physical AI Studio JSON layout. |
| `profiles.so101` | SO-101 follower: model, 14 collision spheres per link, joint setup. |

## Checking one joint (the safe first run)

```
armkit-calibrate check --joint gripper --port /dev/serial/by-id/...            # dry run
armkit-calibrate check --joint gripper --port /dev/serial/by-id/... --go       # moves that joint, asks for YES
armkit-calibrate check --joint shoulder_lift --ends lower --torque-limit 500 ...  # one end only; raise the torque limit for joints that carry weight
```

`check` works on one joint in the frame of the calibration its servo already holds. It saves every joint's stored
calibration to `--backup`, widens only that joint's position limits, finds both travel ends (bounded push, step back on
contact, two agreeing contacts), reports them next to the stored range, then puts the limits, torque state, torque
limit and position back. Nothing is stored; a fault before the joint moved restores it automatically. For joints of the
kinematic chain the arm's pose is taken from the stored calibration and the collision model must call the sweep clear,
otherwise nothing moves and the issue says how far it would get. A sweep the model clears only part of the way is
still searched when the clear part goes past the stored end; the search stops where the clear part ends, and an end
not found by then is `NOT MEASURED` (measure it from a pose that clears more).

## The model frame (needed before any planning)

Planning works in the model's joint angles, but the servos report positions relative to their stored calibration. On a
hand-calibrated arm the two can differ by tens of degrees per joint, and planning on a wrong link plans for a pose the
arm is not in. Record the link once, with the arm held in a described reference pose:

```
armkit-calibrate frame --port ... --pose so101-zero                    # prints what the pose looks like
armkit-calibrate frame --port ... --pose so101-zero --release --go     # releases the arm joints (hold it!), records frame.json, holds again
```

`measure`, `move` and the body-joint `check` take `--frame frame.json` and refuse to plan without it.

A hand-held pose is only as good as the operator's reading of the description: on one SO-101 it came out 27° off on
the shoulder lift although the forearm was right. Prefer offsets measured independently (a camera fit of a marker on
the gripper, or the range midpoints of a URDF built around them), write them as a frame file, and keep the hand-held
direction check for the signs. The sweep check covers everything the search may reach, including angles past the URDF's
joint limits (real arms often travel a few degrees further).

## Measuring the whole arm (the pipeline)

```
armkit-calibrate measure --port ...                      # dry run: lists the joints, bottom-up
armkit-calibrate measure --port ... --frame frame.json --go   # measures every joint end, writes calibration-proposed.json
armkit-calibrate measure --port ... --joints elbow_flex --go
armkit-calibrate restore --port ... --from calibration-proposed.json --go   # later, deliberately: stores it (torque off, arm at rest)
```

`measure` goes from the base outwards. For every end of every joint it plans, with the collision model, where the
other joints must be parked so the sweep is clear (in stages if one pose is not clear all the way), moves there along
checked paths, runs the one-end `check`, and finally returns the arm to its starting pose. It writes a *proposed*
calibration (stored homing offsets, measured ranges) and a report against the stored values; it never writes to the
servos. A joint that carries weight keeps its torque (it would fall otherwise). Its position limits are widened while it
holds (EEPROM lock opened, limits written and read back, torque untouched) so it can go past its stored range; if the
servo refuses that, it is searched inside its stored range only and an end beyond it is an issue (`NOT MEASURED`):
the stored limit is never accepted in place of a measurement. `check` picks a torque limit above twice a joint's holding load.

## Moving to a pose

```
armkit-calibrate move --port ... --set shoulder_lift=0 elbow_flex=0 wrist_flex=0         # plan only: prints the path and closest approach
armkit-calibrate move --port ... --set shoulder_lift=0 elbow_flex=0 wrist_flex=0 --go    # runs it (asks for YES)
```

Angles are relative to the middle of each joint's stored range. The path is checked against the arm's collision model
(self and floor only; a clamp or camera mount is not in it) and played slowly with the guarded path mover.

## Automatic calibration

```
armkit-calibrate plan                         # dry run from the 3D model alone; opens no port
armkit-calibrate run --port /dev/serial/by-id/... --only gripper          # still a dry run
armkit-calibrate run --port /dev/serial/by-id/... --only gripper --go     # moves the arm, asks for YES
armkit-calibrate restore --port ... --from calibration-before.json --go
```

Sequence of `run --go`:

1. The operator confirms the arm rests in the profile's rest pose. The servos' calibration is read and saved to
   `--backup`, then reset (offsets 0, limits full) so an old range cannot clip the search, and a temporary frame is
   written in which the rest pose reads where the model says it should.
2. For each joint, each end of travel (the end nearest the rest pose first): the **other joints are parked** where the
   collision model says the sweep cannot hit the arm or the table (several parking poses in sequence when one pose is
   not clear all the way), by a checked, speed-limited path; then the joint creeps into the end.
3. The joint returns to its rest angle (also staged), its zero re-derived from the measured range.
4. With the arm back at rest and a second confirmation, torque is released and the new offsets and ranges are stored:
   the measured range midpoint becomes the joint's zero. Full-turn joints (a wrist roll) get `0..4095` and keep their
   existing homing offset. Any failure writes the previous calibration back instead.

### Safeguards

- **Bounded push.** The goal never leads the shaft by more than `lead_deg` (default 3), and the servo torque limit is
  set low (default 350 permille) while the procedure runs, so the force on an obstruction is bounded by construction.
- **Step back, don't fail.** A rapid load rise, a load above the ceiling, or a stall stops the joint, backs it off
  `backoff_deg` from where it actually is and retries slower. An end counts as found when two contacts agree; contacts
  that never repeat (a hand, a cable) end as `UNCONFIRMED` at the most conservative position and are reported, not raised.
  The same happens for moves between poses; after `max_events` the arm steps back once more and holds.
- **Model-aware.** Parking poses are chosen against the collision model with margins (10 mm, then 5 mm, then 0) and with
  assumed angle error (10° for joints not yet measured, 3° after), clamped to joint limits. Search steps are vetoed at
  runtime if the estimated pose would collide. The plan reports the margin it achieved; a sweep with no clear plan is
  an issue, and a plan with issues is never run.
- **Only a servo fault raises** (error flags, temperature, no answer). It stops where it is, leaves torque on, writes
  nothing more and says how to restore. Nothing retries a fault.
- Encoder seam, travel cap and per-search time limit end a search that would otherwise run on. Torque limit is restored
  to full only after the calibration is stored.

### Status and limits

Everything above is tested against the simulated bus and a fake SDK. On real servos only `check` has been run (SO-101
follower gripper: both ends found, reproducibly, within 0.8 deg of Studio's stored range); the full `run` has not. The load
and stall thresholds, torque limit, speeds and the SO-101 rest pose (Studio's setup-wizard "home" pose) are starting
values: do a first supervised run with `--only gripper`, watch the load, then widen. Collision shapes are conservative
bounding spheres; the tightest planned sweep on the SO-101 is the shoulder-lift forward swing (two stages, 0 mm margin).
A freshly modelled arm needs the rest pose and joint travel in its profile to match the real arm.

## Python

```python
from armkit.feetech import FeetechBus
from armkit.procedure import CalibrationSettings, plan_calibration, run_calibration
from armkit.profiles.so101 import so101_profile
from armkit.servo import RealClock

profile = so101_profile()
plan = plan_calibration(profile, CalibrationSettings())
print(plan.describe())
with FeetechBus(port, {j.name: j.servo_id for j in profile.joints}, acceleration=40) as bus:
	result = run_calibration(
		bus, profile, plan=plan, clock=RealClock(), confirm=lambda message: input(message + " ") == "YES"
	)
```

`SimulatedBus` implements the same interface for tests and dry experiments.

## A new robot

1. `model = load_urdf(path, end_link=..., tool_link=...)`.
2. `collision = collision_from_urdf(path, model, spheres_per_link=14, attach={...})`, then bake the spheres as numbers
   (see `profiles/so101.py`), ignore link pairs that touch by design (`ignoring_contacts_at(rest_pose)`), set the floor.
3. Describe each servo joint in a `JointSetup` (id, rest angle, kind, optional travel / parking joints) and wrap
   everything in an `ArmProfile`; list joints in the order to calibrate (typically outermost first).
