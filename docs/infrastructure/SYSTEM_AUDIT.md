# System audit

Audit performed 13 November 2026 over SSH. Ubuntu 26.04.1 LTS, kernel 7.0.0-38-generic, x86_64; Intel Core Ultra X9 388H, 16 CPUs; 61 GiB RAM, 8 GiB swap and 874 GiB available root storage at audit time.

Intel Arc B390 GPU PCI 8086:b080 and Panther Lake NPU 8086:b03e appear, with `/dev/dri/renderD128` and `/dev/accel/accel0`. The USB HP 5MP Camera 30c9:00fb presents video0/1 and HP IR Camera video2/3. Formats and actual capture or inference have not been tested. The system Python did not have OpenCV or OpenVINO modules. Intel GPU tools and microcode were found; deeper SDK and demo inventory remains incomplete.

Tailscale is active at 100.76.18.70; a direct path was observed from one Mac. `junction-ssh.service` listens on that address on port 22 and is enabled. The host key was checked against the workstation console and admin key login succeeded. The original service and socket were runtime masked during installation; the separate port 2222 listener is temporary. Reboot behavior is untested. UFW was inactive and no firewall changes were made. `intel` has sudo; dev1–dev4 have separate home directories and no sudo.

Git 2.53.0, tmux 3.6, Python 3.14.4 and Python venv with pip are installed and tested. Node and Claude were not found on the inspected PATH. GitHub authentication from Ubuntu is pending.
