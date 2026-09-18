# Security Policy

## Supported versions

Security fixes target the latest release on `main`.

## Report privately

Do not open a public issue for a vulnerability. Use GitHub's private vulnerability reporting for `DailenG/omarchtober` and include affected version, reproduction, impact, and suggested mitigation when available.

## Trust boundaries

Omarchtober runs as the current user without privilege escalation.

- Runtime makes no network requests.
- Plugin source and `/usr/share/omarchy` are read-only.
- Configuration is capped at 256 KiB and normalized independently by QML and Python.
- Terminal allocation is capped at 500×200 cells; every entity population is bounded.
- Custom media must be an absolute, local, regular, non-symlink file with an allowlisted extension and 2 GiB ceiling.
- Custom media is passed to `mpv` as an argv item after `--`; no shell interpretation occurs.
- Audio leadership uses a private mode-0700 directory and no-follow mode-0600 lock.
- Idle integration removes only a stock-screensaver toggle whose contents match Omarchtober's private ownership marker.
- External bug-report navigation occurs only after direct user action.

## External tools

The launcher uses current Omarchy, Hyprland, a supported terminal, `jq`, and `socat`. Procedural audio uses `pw-cat`; custom media uses `mpv`; the graphical media picker uses `zenity`. Missing optional tools fail closed with a diagnostic.

## Out of scope

A local attacker who can replace the user's plugin checkout, Python interpreter, Omarchy binaries, terminal, PipeWire tools, or `mpv` already has equivalent user-level code execution. Vulnerabilities in those upstream components should be reported upstream.
