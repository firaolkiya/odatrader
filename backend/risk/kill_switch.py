# backend/risk/kill_switch.py
from datetime import datetime, date
import os

KILL_SWITCH_FILE = "kill_switch.flag"
KILL_SWITCH_TIMESTAMP_FILE = "kill_switch_timestamp.txt"

def activate_kill_switch():
    with open(KILL_SWITCH_FILE, "w") as f:
        # Store the date (YYYY-MM-DD) when the kill switch was triggered
        f.write(date.today().isoformat())

def is_kill_switch_active():
    if not os.path.exists(KILL_SWITCH_FILE):
        return False
    
    with open(KILL_SWITCH_FILE, "r") as f:
        try:
            kill_date = date.fromisoformat(f.read().strip())
            if date.today() > kill_date:
                os.remove(KILL_SWITCH_FILE)  # New day has started; reset
                return False
            return True
        except Exception:
            return True  # Treat as active if file is corrupted

def deactivate_kill_switch():
    today = datetime.utcnow().date()

    # If timestamp file exists, read the last date
    if os.path.exists(KILL_SWITCH_TIMESTAMP_FILE):
        with open(KILL_SWITCH_TIMESTAMP_FILE, 'r') as f:
            last_date_str = f.read().strip()
            try:
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            except ValueError:
                last_date = None
    else:
        last_date = None

    # If it's a new day, remove kill switch
    if last_date is None or today > last_date:
        if os.path.exists(KILL_SWITCH_FILE):
            os.remove(KILL_SWITCH_FILE)
            print("[KILL SWITCH] Deactivated (new day)")

        # Update timestamp file to today
        with open(KILL_SWITCH_TIMESTAMP_FILE, 'w') as f:
            f.write(today.strftime("%Y-%m-%d"))
