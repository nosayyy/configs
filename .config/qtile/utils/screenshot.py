#!/usr/bin/env python3
import sys, os
from datetime import datetime

from PyQt6.QtWidgets import QApplication

SCREENSHOT_DIR = os.path.expanduser("~/Pictures")

def take_full():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    pixmap = screen.grabWindow(0)
    filename = os.path.join(SCREENSHOT_DIR, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    pixmap.save(filename)
    app.quit()

def take_area():
    # Заглушка – в будущем можно добавить обрезку
    take_full()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "area":
        take_area()
    else:
        take_full()