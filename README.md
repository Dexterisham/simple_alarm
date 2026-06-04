# Simple CLI Alarm Clock

A lightweight, command-line interface (CLI) alarm clock application for Windows. It lets you schedule alarms using relative durations (e.g., `10s`, `5m`, `1h 30m`) or absolute times (e.g., `14:30`, `2:30 PM`). It supports running silently in the background and will automatically pop open a new window when the alarm triggers.

---

## 🚀 Quick Start (Choose How to Run)

### Option 1: Standalone Executable (Easiest - No Python Installation Needed!)
We have pre-compiled the alarm clock into a standalone executable. You can access it directly here: **[alarm.exe](dist/alarm.exe)**.

1. Open PowerShell or Command Prompt.
2. Run the executable:
   ```bash
   # Run in current terminal (Foreground)
   .\dist\alarm.exe 10s

   # Run silently in background (Spawns a window when finished!)
   .\dist\alarm.exe 10s -b
   ```

---

### Option 2: Running with Python Directly (No Installation Needed)
If you have Python installed, you can run the script file directly.

1. Open PowerShell or Command Prompt in this folder.
2. Run the script:
   ```bash
   # Run in current terminal (Foreground)
   python alarm.py 10s

   # Run silently in background (Spawns a window when finished!)
   python alarm.py 10s -b
   ```

---

### Option 3: Global Installation (Run from anywhere on your computer)
You can install the app globally so you can type `simple-alarm` in any folder or terminal.

1. Open terminal and run:
   ```bash
   pip install .
   ```
2. Now, you can run it from any terminal session:
   ```bash
   # Run in current terminal (Foreground)
   simple-alarm 10s

   # Run silently in background (Spawns a window when finished!)
   simple-alarm 10s -b
   ```

---

## ⏱️ Alarm Time Formats

When running the alarm, you can specify times in these formats:

* **Seconds**: `10s` (goes off in 10 seconds)
* **Minutes**: `5m` (goes off in 5 minutes)
* **Hours & Minutes**: `1h 30m` (goes off in 1.5 hours)
* **Numbers only**: `15` (defaults to 15 minutes)
* **Clock Time (24-Hour)**: `14:30` (goes off at exactly 2:30 PM local time)
* **Clock Time (12-Hour)**: `2:30 PM` or `2:30PM`

> [!TIP]
> If you run the command without specifying any time arguments (e.g., just type `simple-alarm` or `.\dist\alarm.exe`), the program will interactively ask you to type the alarm time.

---

## 🔔 Alarm Control Actions

When the alarm finishes waiting, it will ring and show:
```text
========================================
!!!  ALARM TRIGGERED!  !!!
========================================

Press Enter to Dismiss, or type 's' to Snooze (5 min):
```

* **Snooze**: Type `s` and press **Enter**. The alarm turns off, reschedules a new background wait for **5 minutes**, and the window closes.
* **Dismiss**: Just press **Enter** (no text). The alarm turns off and exits.
* **Stop Early**: Press `Ctrl + C` in the terminal at any time.

---

## 🗑️ Cleanup & Uninstall

### To Uninstall the Global Package:
```powershell
pip uninstall simple-alarm -y
rmdir /s /q simple_alarm.egg-info
```

### To Delete Built Executable & Temporary Files:
```powershell
rmdir /s /q build
rmdir /s /q dist
del alarm.spec
```

---

## 🛠️ Developer Reference (Optional)

### CLI Command Options
```text
usage: simple-alarm [-h] [-b] [--daemon-wait EPOCH_TIME] [--trigger] [time_input]

positional arguments:
  time_input            Alarm time or duration (e.g. 10s, 5m, 14:30)

options:
  -h, --help            show this help message and exit
  -b, --background      Run the alarm waiting process in the background
  --daemon-wait EPOCH_TIME
                        Internal: wait silently in background until timestamp
  --trigger             Internal: trigger foreground alarm and sound
```

### Rebuilding Standalone Executable
If you modify the source code, rebuild the EXE using:
```bash
pip install pyinstaller
pyinstaller --onefile alarm.py
```
