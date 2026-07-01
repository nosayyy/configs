#!/usr/bin/env python3

import os
import sys
import shlex

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QListWidget,
    QVBoxLayout,
    QWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, QEvent, QProcess
from PyQt6.QtGui import QFont, QColor, QPalette


# Directories where .desktop files are stored
APP_DIRS = [
    "/usr/share/applications",
    os.path.expanduser("~/.local/share/applications"),
]


def load_desktop_applications():
    """
    Scan standard directories for .desktop files and extract application
    names and executable commands.

    Returns:
        list of (name, command) tuples, sorted alphabetically by name.
    """
    applications = []
    for directory in APP_DIRS:
        if not os.path.isdir(directory):
            continue
        for entry in os.scandir(directory):
            if not entry.name.endswith(".desktop"):
                continue
            try:
                with open(entry.path, "r") as file:
                    name = None
                    command = None
                    for line in file:
                        line = line.strip()
                        if line.startswith("Name="):
                            name = line.split("=", 1)[1].strip()
                        elif line.startswith("Exec="):
                            # Remove field codes like %F, %U, etc.
                            command = line.split("=", 1)[1].split("%")[0].strip()
                        if name and command:
                            applications.append((name, command))
                            break
            except (OSError, UnicodeDecodeError):
                # Skip files that cannot be read
                continue
    return sorted(applications, key=lambda x: x[0].lower())


class Launcher(QMainWindow):
    """A frameless, semi-transparent launcher window with search and list."""

    def __init__(self):
        super().__init__()
        self._applications = load_desktop_applications()
        self._setup_ui()
        self._populate_list("")

    def _setup_ui(self):
        """Configure the window appearance, layout, and event filters."""
        # Window flags and geometry
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(600, 450)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(
            (screen_geometry.width() - 600) // 2,
            (screen_geometry.height() - 450) // 2,
        )

        # Dark translucent palette
        self._apply_dark_palette()

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)

        # Search input field
        self.search_field = QLineEdit()
        self.search_field.setFont(QFont("sans", 16))
        self.search_field.setPlaceholderText("Search...")
        self.search_field.setStyleSheet(
            "background: transparent; border: none; color: white; padding: 8px; font-size: 18px;"
        )
        self.search_field.textChanged.connect(self._populate_list)
        layout.addWidget(self.search_field)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setFont(QFont("sans", 14))
        self.results_list.setStyleSheet(
            "background: transparent; border: none; color: white; outline: none;"
        )
        self.results_list.itemActivated.connect(self._launch_application)
        layout.addWidget(self.results_list)

        # Event filters for keyboard shortcuts
        self.search_field.installEventFilter(self)
        self.results_list.installEventFilter(self)

    def _apply_dark_palette(self):
        """Set a dark semi-transparent colour scheme."""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 200))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30, 200))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(60, 60, 60))
        self.setPalette(palette)
        self.setStyleSheet("border-radius: 12px; background-color: rgba(0,0,0,200);")

    def _populate_list(self, filter_text: str):
        """
        Filter applications by case-insensitive substring and update the list.

        Args:
            filter_text: Text to match against application names.
        """
        self.results_list.clear()
        filter_lower = filter_text.lower()
        for name, command in self._applications:
            if filter_lower in name.lower():
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, command)
                self.results_list.addItem(item)
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def _launch_application(self, item: QListWidgetItem):
        """
        Launch the application associated with the given list item.

        The command string is split into program and arguments using shlex.
        If splitting fails, the whole string is used as the program (fallback).

        Args:
            item: The selected list item containing the command in UserRole.
        """
        command = item.data(Qt.ItemDataRole.UserRole)
        try:
            args = shlex.split(command)
        except ValueError:
            # Fallback to the old behaviour (single command with no arguments)
            args = [command]
        if args:
            QProcess.startDetached(args[0], args[1:])
        self.close()

    def eventFilter(self, source, event):
        """
        Handle keyboard shortcuts:
        - Escape → close the window.
        - Enter/Return in search field → launch the selected application.
        - Down arrow in search field → move focus to the list.
        """
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Escape:
                self.close()
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if source is self.search_field and self.results_list.count() > 0:
                    self._launch_application(self.results_list.currentItem())
                    return True
                # Enter on the list is already handled by itemActivated signal
            if key == Qt.Key.Key_Down and source is self.search_field:
                if self.results_list.count() > 0:
                    self.results_list.setFocus()
                    self.results_list.setCurrentRow(0)
                    return True
        return super().eventFilter(source, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    app.exec()