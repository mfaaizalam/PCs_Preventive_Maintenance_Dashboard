# Agent relaunch task (audit pause/resume)

This is what makes the dashboard's "Pause for audit" / "Resume" buttons
work without anyone touching each PC by hand. It is intentionally boring
and visible - nothing here is meant to be hidden from Task Manager, Task
Scheduler, or an auditor.

## How it behaves

- Normal operation: the agent runs continuously, exactly as before.
- When an IT Manager clicks **Pause**, the agent acks the request and
  calls `sys.exit(0)` on its next check-in - it is genuinely not running.
- A Scheduled Task named **"Lab Monitoring Agent - Relaunch Check"**
  starts the agent exe every 5 minutes. Each time, the agent's very first
  action (`check_pause_state_or_exit`) is a single lightweight status
  call to the server:
  - still paused -> it logs that, then exits immediately (no data
    collection at all while paused).
  - resume was requested -> it acks and continues running normally
    until told otherwise.
- During an audit, a technician (or the auditor) can open Task Scheduler
  and see this task, its schedule, and its description in plain text.
  There is nothing to explain away - the task's whole job is described
  right there.

## One-time setup per PC (run once, as Administrator)

```bat
schtasks /Create ^
  /TN "Lab Monitoring Agent - Relaunch Check" ^
  /TR "\"C:\Program Files\LabAgent\agent.exe\"" ^
  /SC MINUTE /MO 5 ^
  /RU SYSTEM ^
  /RL HIGHEST ^
  /F
```

Adjust the `/TR` path to wherever `agent.exe` is actually installed.
`/RU SYSTEM` keeps it running whether or not anyone is logged in;
swap to a specific service account if your environment requires that.

## Removing it (if a lab is retired or the agent is uninstalled)

```bat
schtasks /Delete /TN "Lab Monitoring Agent - Relaunch Check" /F
```

## Why not just "hide" the process instead?

Because the actual audit requirement is "no extra software running" -
and this satisfies that literally: for the whole pause window the agent
process does not exist except for a few seconds every 5 minutes to check
one flag. A hidden/no-log process that keeps running in the background
would still be extra software running, just undetected - that fails the
audit's actual intent even if it passes a casual glance, and it's not
something this project builds.