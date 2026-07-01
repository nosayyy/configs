#!/usr/bin/env python3
import subprocess, sys

def adjust(direction):
    if direction == "up":
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+5%"])

    elif direction == "down":
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"])
        
    elif direction == "mute":
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        adjust(sys.argv[1])