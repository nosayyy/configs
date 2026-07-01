#!/usr/bin/env python3

import sys
import signal

from pydbus import SessionBus

from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


# Default timeout in milliseconds
DEFAULT_TIMEOUT_MS = 5000

# Geometry constants
WIDGET_WIDTH = 380
WIDGET_HEIGHT = 100
MARGIN_FROM_EDGE = 20


class NotificationPopup(QWidget):
    """
    A frameless, translucent popup that displays a notification.
    It appears in the top‑right corner of the screen and disappears
    after a configurable timeout.
    """

    def __init__(self, summary: str, body: str):
        """
        Args:
            summary: Notification title (bold).
            body:    Notification text (wrapped).
        """
        super().__init__()
        self._setup_window()
        self._build_ui(summary, body)
        self._position_on_screen()

    def _setup_window(self):
        """Configure window flags and transparency."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(WIDGET_WIDTH, WIDGET_HEIGHT)
        self.setStyleSheet(
            "background-color: rgba(20, 20, 20, 220);"
            "border-radius: 12px;"
            "color: white;"
        )

    def _build_ui(self, summary: str, body: str):
        """Create the layout with title and body labels."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        title_label = QLabel(summary)
        title_label.setFont(QFont("sans", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("background: transparent;")
        layout.addWidget(title_label)

        body_label = QLabel(body)
        body_label.setFont(QFont("sans", 12))
        body_label.setWordWrap(True)
        body_label.setStyleSheet("background: transparent;")
        layout.addWidget(body_label)

        self.setLayout(layout)

    def _position_on_screen(self):
        """Place the widget in the top‑right corner of the primary screen."""
        screen = QApplication.primaryScreen().geometry()
        x      = screen.width() - self.width() - MARGIN_FROM_EDGE
        y      = MARGIN_FROM_EDGE
        self.move(x, y)

    def show_with_timeout(self, timeout_ms: int):
        """
        Show the popup and schedule its dismissal.

        Args:
            timeout_ms: Time in milliseconds before hiding.
                        If negative, the popup stays visible indefinitely.
        """
        self.show()
        if timeout_ms >= 0:
            QTimer.singleShot(timeout_ms, self._dismiss)

    def _dismiss(self):
        """Hide and delete the widget."""
        self.hide()
        self.deleteLater()


class NotificationsDaemon:
    """
    DBus service object that implements the notification interface.
    Each method corresponds to a DBus method of org.freedesktop.Notifications.
    """

    def __init__(self, bus):
        self.bus = bus
        # A simple counter for notification IDs (if needed)
        self._next_id = 1

    def Notify(
        self,
        app_name:    str,
        replaces_id: int,
        app_icon:    str,
        summary:     str,
        body:        str,
        actions:     list,
        hints:       dict,
        timeout:     int,
    ) -> int:
        """
        Display a notification popup.

        Args:
            app_name:     Name of the calling application (ignored).
            replaces_id:  ID of a notification to replace (ignored).
            app_icon:     Icon name/path (ignored).
            summary:      Title of the notification.
            body:         Message text.
            actions:      List of action names (ignored).
            hints:        Additional hints (ignored).
            timeout:      Timeout in milliseconds.
                          0 means use default, -1 means infinite.

        Returns:
            A unique notification ID (always 1 in this simple implementation).
        """
        # Normalise timeout: 0 → default value
        if timeout == 0:
            timeout = DEFAULT_TIMEOUT_MS

        popup = NotificationPopup(summary, body)
        popup.show_with_timeout(timeout)

        # Return a simple ID (consistent with original code)
        return 1

    def CloseNotification(self, notification_id: int):
        """
        Close a notification by its ID.
        This implementation does not keep track of active popups, so it does nothing.
        """
        pass

    def GetCapabilities(self) -> list:
        """Return the capabilities supported by this daemon."""
        return ["body"]   # Minimal set

    def GetServerInformation(self) -> tuple:
        """
        Return information about the notification server.

        Returns:
            (name, vendor, version, spec_version)
        """
        return ("qtile-notifier", "Qtile", "1.0", "1.2")


if __name__ == "__main__":
    # Create Qt application
    app = QApplication(sys.argv)

    # Connect to the session bus and publish the daemon
    bus = SessionBus()
    daemon = NotificationsDaemon(bus)
    bus.publish("org.freedesktop.Notifications", "/org/freedesktop/Notifications", daemon)

    print("Notification daemon started", flush=True)

    # Restore default SIGINT handling to allow Ctrl+C to quit
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Start the event loop
    app.exec()