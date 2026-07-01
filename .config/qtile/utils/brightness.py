#!/usr/bin/env python3
import sys, os

def get_device():
    base = "/sys/class/backlight/"

    for dev in os.listdir(base):
        if os.path.isfile(os.path.join(base, dev, "brightness")):
            return os.path.join(base, dev)
        
    raise FileNotFoundError("No backlight device found")

def adjust(direction):
    dev = get_device()
    
    with open(os.path.join(dev, "max_brightness")) as f:
        max_val = int(f.read().strip())

    with open(os.path.join(dev, "brightness")) as f:
        cur = int(f.read().strip())

    step = max_val // 20
    new = min(cur + step, max_val) if direction == "up" else max(cur - step, 1)

    with open(os.path.join(dev, "brightness"), "w") as f:
        f.write(str(new))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        adjust(sys.argv[1])