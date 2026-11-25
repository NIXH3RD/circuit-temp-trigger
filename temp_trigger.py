"""
Temperature trigger (Manual + Auto)
- Runs circuit_analysis.py when temperature reaches 35 C or above
- Re-arms only after temperature drops to 30 C or below

Run: python temp_trigger.py
Serial auto mode needs: pip install pyserial
"""
import subprocess
import sys
import time
from pathlib import Path

LOW_C = 30.0     # re-arm at or below this
HIGH_C = 35.0    # trigger at or above this
CHECK_EVERY_S = 1.0
SCRIPT = Path(__file__).with_name("circuit_analysis.py")


def manual_reader():
    def read():
        raw = input("Temperature (C) [q = quit]: ").strip().lower()
        if raw in ("q", "quit", "exit"):
            raise KeyboardInterrupt
        return float(raw)
    return read


def sim_reader():
    state = {"t": 28.0, "dir": 1}

    def read():
        state["t"] += 0.5 * state["dir"]
        if state["t"] >= 38:
            state["dir"] = -1
        elif state["t"] <= 27:
            state["dir"] = 1
        return state["t"]
    return read


def serial_reader():
    import serial  # pip install pyserial
    port = input("Serial port (e.g. COM3): ").strip() or "COM3"
    ser = serial.Serial(port, 9600, timeout=2)

    def read():
        return float(ser.readline().decode(errors="ignore").strip())
    return read


def run_action():
    print(f"  >>> Triggered! Running {SCRIPT.name}")
    subprocess.Popen([sys.executable, str(SCRIPT)])


def choose_mode():
    print("Select mode")
    print("  1) Manual - type the temperature yourself")
    print("  2) Auto   - simulated temperature (for testing)")
    print("  3) Auto   - Arduino/sensor (serial)")
    while True:
        c = input("Choose [1/2/3]: ").strip()
        if c == "1":
            return manual_reader(), False
        if c == "2":
            return sim_reader(), True
        if c == "3":
            return serial_reader(), True
        print("Please enter 1, 2 or 3")


def main():
    read, is_auto = choose_mode()
    armed = True
    print(f"\nTrigger at >= {HIGH_C} C, re-arm at <= {LOW_C} C (Ctrl+C = stop)\n")
    try:
        while True:
            try:
                t = read()
            except ValueError:
                print("  Please enter a number")
                continue
            state = "ARMED" if armed else "waiting to cool"
            print(f"{time.strftime('%H:%M:%S')}  {t:5.1f} C  [{state}]")

            if armed and t >= HIGH_C:
                run_action()
                armed = False
            elif not armed and t <= LOW_C:
                armed = True
                print("  Cooled down -> re-armed")

            if is_auto:
                time.sleep(CHECK_EVERY_S)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
