import os
import re
import sys
import time
import datetime
import threading
import winsound
import argparse
import subprocess

beeping = False

def ring_beeps():
    """
    Runs in a background thread to play the beep sound continuously 
    while the main thread waits for user input.
    """
    global beeping
    while beeping:
        try:
            winsound.Beep(1000, 400)  # Frequency: 1000Hz, Duration: 400ms
        except Exception:
            pass
        time.sleep(0.1)  # Silence gap between beeps


def parse_input(user_input):
    """
    Parses duration (e.g. 5m, 10s, 1h 30m) or absolute time (e.g. 14:30, 2:30 PM).
    """
    user_input = user_input.strip().lower()
    
    # Check if input is a relative duration
    duration_sec = 0
    matched = False
    
    hours_match = re.search(r'(\d+)\s*h', user_input)
    minutes_match = re.search(r'(\d+)\s*m', user_input)
    seconds_match = re.search(r'(\d+)\s*s', user_input)
    
    if hours_match:
        duration_sec += int(hours_match.group(1)) * 3600
        matched = True
    if minutes_match:
        duration_sec += int(minutes_match.group(1)) * 60
        matched = True
    if seconds_match:
        duration_sec += int(seconds_match.group(1))
        matched = True
        
    if matched:
        return datetime.datetime.now() + datetime.timedelta(seconds=duration_sec)
        
    # Check if raw number (default to minutes)
    if user_input.isdigit():
        minutes = int(user_input)
        return datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        
    # Check if absolute clock time
    user_input = user_input.upper()
    formats = [
        "%H:%M",          # 14:30
        "%I:%M %p",       # 02:30 PM / 2:30 PM
        "%I:%M%p",        # 2:30PM
        "%H:%M:%S",       # 14:30:00
        "%I:%M:%S %p",    # 2:30:00 PM
        "%I:%M:%S%p",     # 2:30:00PM
    ]
    
    for fmt in formats:
        try:
            t = datetime.datetime.strptime(user_input, fmt).time()
            now = datetime.datetime.now()
            target = datetime.datetime.combine(now.date(), t)
            if target <= now:
                target += datetime.timedelta(days=1)
            return target
        except ValueError:
            continue
            
    raise ValueError("Unsupported format. Use e.g. '10s', '5m', '14:30', or '2:30 PM'")


def run_countdown(target_time):
    """
    Simple ticker that displays remaining time on a single line.
    """
    while True:
        now = datetime.datetime.now()
        if now >= target_time:
            break
            
        remaining = target_time - now
        total_sec = int(remaining.total_seconds())
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        
        # \r moves the cursor back to the start of the line to overwrite it
        print(f"Time remaining: {h:02d}:{m:02d}:{s:02d}", end="\r")
        time.sleep(0.5)
    
    print("Time remaining: 00:00:00")


def get_executable_command():
    """
    Returns the base command list required to invoke this program again.
    Handles running as script (e.g. python alarm.py) and as entrypoint (e.g. simple-alarm).
    """
    if sys.argv[0].endswith('.py'):
        return [sys.executable, os.path.abspath(sys.argv[0])]
    else:
        return [sys.argv[0]]


def parse_args():
    """
    Parses CLI arguments.
    """
    parser = argparse.ArgumentParser(description="Simple CLI Alarm Clock")
    parser.add_argument("time_input", nargs="?", default=None,
                        help="Alarm time (e.g. 14:30, 2:30 PM) or duration (e.g. 10s, 5m)")
    parser.add_argument("-b", "--background", action="store_true",
                        help="Run the alarm waiting process in the background")
    parser.add_argument("--daemon-wait", type=float, metavar="EPOCH_TIME",
                        help="Internal use: wait silently until epoch timestamp, then trigger alarm console")
    parser.add_argument("--trigger", action="store_true",
                        help="Internal use: trigger foreground alarm and sound")
    return parser.parse_args()


def run_daemon_wait(target_timestamp):
    """
    Waits silently until the epoch timestamp, then triggers a new console.
    """
    while True:
        now = time.time()
        if now >= target_timestamp:
            break
        sleep_sec = min(target_timestamp - now, 5.0)
        if sleep_sec > 0:
            time.sleep(sleep_sec)
            
    # Spawn the interactive alarm console in a new console window
    cmd = get_executable_command() + ["--trigger"]
    # CREATE_NEW_CONSOLE = 0x00000010
    subprocess.Popen(cmd, creationflags=0x00000010)


def run_alarm_trigger():
    """
    Active foreground alarm console: plays beep sound and prompts user to snooze or dismiss.
    """
    global beeping
    print("\n" + "=" * 40)
    print("!!!  ALARM TRIGGERED!  !!!")
    print("=" * 40 + "\n")
    
    beeping = True
    sound_thread = threading.Thread(target=ring_beeps, daemon=True)
    sound_thread.start()
    
    try:
        choice = input("Press Enter to Dismiss, or type 's' to Snooze (5 min): ").strip().lower()
    except KeyboardInterrupt:
        choice = ''
        print("\nAlarm dismissed.")
        
    beeping = False
    sound_thread.join(timeout=1.0)
    
    if choice == 's':
        snooze_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        # Spawn new daemon wait process in the background
        cmd = get_executable_command() + ["--daemon-wait", str(snooze_time.timestamp())]
        # CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(cmd, creationflags=0x08000000)
        
        print(f"\nSnoozed! Alarm will sound again at {snooze_time.strftime('%I:%M:%S %p')}.")
        time.sleep(2.5)
    else:
        print("\nAlarm dismissed. Goodbye!")
        time.sleep(1.0)


def main():
    args = parse_args()
    
    if args.daemon_wait is not None:
        run_daemon_wait(args.daemon_wait)
        return

    if args.trigger:
        run_alarm_trigger()
        return

    # Standard setup/parsing flow
    user_input = args.time_input
    if not user_input:
        print("--- Simple CLI Alarm ---")
        user_input = input("Enter alarm time (e.g. 14:30, 2:30 PM) or duration (e.g. 10s, 5m): ")
    
    try:
        target_time = parse_input(user_input)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1 if args.time_input else 0)

    target_timestamp = target_time.timestamp()
    formatted_time = target_time.strftime('%I:%M:%S %p')

    if args.background:
        cmd = get_executable_command() + ["--daemon-wait", str(target_timestamp)]
        # CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(cmd, creationflags=0x08000000)
        print(f"Alarm scheduled in background for {formatted_time}.")
        return

    # Normal foreground countdown flow
    print(f"Alarm scheduled for {formatted_time}")
    
    global beeping
    while True:
        # 1. Run the countdown to target
        run_countdown(target_time)
        
        # 2. Ring the alarm
        beeping = True
        sound_thread = threading.Thread(target=ring_beeps, daemon=True)
        sound_thread.start()
        
        # 3. Wait for user snooze or dismiss action
        try:
            choice = input("\n[ALARM TRIGGERED] Press Enter to Dismiss, or type 's' to Snooze (5 min): ").strip().lower()
        except KeyboardInterrupt:
            choice = ''
            print("\nAlarm dismissed.")
            beeping = False
            sound_thread.join(timeout=1.0)
            break
            
        # Stop sound
        beeping = False
        sound_thread.join(timeout=1.0)
        
        if choice == 's':
            target_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
            print(f"\nSnoozed! Alarm will sound again at {target_time.strftime('%I:%M:%S %p')}.\n")
        else:
            print("\nAlarm dismissed. Goodbye!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAlarm stopped. Goodbye!")
        sys.exit(0)
