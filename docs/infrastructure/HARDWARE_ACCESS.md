# Hardware access

The HP 5MP USB camera is mapped to /dev/video0 and /dev/video1, and its IR camera to /dev/video2 and /dev/video3. Intel Arc B390 GPU and Panther Lake NPU devices are present; see SYSTEM_AUDIT. Camera usage, formats and runtime support have not been confirmed. Do not assume `/dev/video0` or add users to device groups without an explicit access decision. Do not kill camera processes, replace drivers or change the kernel.

Once access is available, inventory `/dev/video*`, `lsusb`, `lspci -nn`, `/dev/dri`, `/dev/accel`, existing Intel runtimes, and camera owners. Use `v4l2-ctl --list-devices` and per-device format enumeration if installed; do not install it blindly. Test capture only if safe and permitted. Confirm GPU/NPU runtime support with an actual workload before claiming it works.

Proposed direction, subject to project requirements: one local camera owner publishes frames or results to authorized local consumers, with recorded sample frames for independent development. No service has been built or started. Coordinate exclusive use of cameras and heavyweight inference jobs until actual resource capacity is known.
