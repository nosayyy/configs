//@ pragma IconTheme Colloid-Green-Catppuccin-Dark
import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import QtQuick

ShellRoot {
    id: root

    // ──────────────────────────────────────────────────────────────
    // MORPHING ISLAND - The main UI element
    // ──────────────────────────────────────────────────────────────
    
    MorphingIsland {
        id: morphingIsland
    }

    // ──────────────────────────────────────────────────────────────
    // SYSTEM MONITORING & STATE MANAGEMENT
    // ──────────────────────────────────────────────────────────────

    // CPU Monitoring
    Process {
        id: cpuProcess
        command: ["sh", "-c", "head -1 /proc/stat"]
        running: true
        stdout: SplitParser {
            onRead: (data) => {
                if (!data) return
                var parts = data.trim().split(/\s+/)
                var idle = parseInt(parts[4]) + parseInt(parts[5])
                var total = parts.slice(1, 8).reduce((acc, val) => acc + parseInt(val), 0)
                if (root._lastTotal > 0 && total > root._lastTotal) {
                    var cpuPct = Math.round(100 * (1 - (idle - root._lastIdle) / (total - root._lastTotal)))
                    SystemStats.cpuPct = cpuPct
                }
                root._lastIdle = idle
                root._lastTotal = total
            }
        }
    }
    
    property int _lastIdle: 0
    property int _lastTotal: 0
    
    Timer {
        interval: 2000
        running: true
        repeat: true
        onTriggered: cpuProcess.running = true
    }

    // RAM Monitoring
    Process {
        id: ramProcess
        command: ["sh", "-c", "free | grep Mem"]
        running: true
        stdout: SplitParser {
            onRead: (data) => {
                if (!data) return
                var parts = data.trim().split(/\s+/)
                var usedMem = parseInt(parts[2]) || 0
                SystemStats.ramPct = Math.round((usedMem / parseInt(parts[1])) * 100)
            }
        }
    }
    
    Timer {
        interval: 3000
        running: true
        repeat: true
        onTriggered: ramProcess.running = true
    }

    // Temperature Monitoring
    Process {
        id: tempProcess
        command: ["sh", "-c", "cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0"]
        running: true
        stdout: SplitParser {
            onRead: (data) => {
                if (!data) return
                var tempRaw = parseInt(data.trim()) || 0
                // Convert from millidegrees to celsius
                SystemStats.cpuTemp = Math.round(tempRaw / 1000)
            }
        }
    }
    
    Timer {
        interval: 5000
        running: true
        repeat: true
        onTriggered: tempProcess.running = true
    }

    // Volume Monitoring
    Process {
        id: volumeProcess
        command: ["sh", "-c", "wpctl get-volume @DEFAULT_SINK@"]
        running: true
        stdout: SplitParser {
            onRead: (data) => {
                if (!data) return
                IslandState.volumeMuted = data.indexOf("MUTED") !== -1
                var match = data.match(/([\d.]+)/)
                if (match) {
                    IslandState.volumeLevel = Math.min(parseFloat(match[1]), 1.5)
                }
            }
        }
    }
    
    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: volumeProcess.running = true
    }

    // Brightness Monitoring
    Process {
        id: brightnessProcess
        command: ["sh", "-c", "echo $(brightnessctl get) && echo $(brightnessctl max)"]
        running: true
        stdout: SplitParser {
            property int _line: 0
            onRead: (data) => {
                if (!data) return
                var value = parseInt(data.trim()) || 0
                if (this._line === 0) {
                    root._brightnessCurrent = value
                } else {
                    root._brightnessMax = value
                    IslandState.brightnessLevel = Math.max(0, Math.min(1, root._brightnessCurrent / value))
                }
                this._line = (this._line + 1) % 2
            }
            Component.onCompleted: _line = 0
        }
    }
    
    property int _brightnessCurrent: 0
    property int _brightnessMax: 255
    
    Timer {
        interval: 2000
        running: true
        repeat: true
        onTriggered: brightnessProcess.running = true
    }

    // Network Status Monitoring
    Process {
        id: networkProcess
        command: ["sh", "-c", "nmcli radio wifi"]
        running: true
        stdout: SplitParser {
            onRead: (data) => {
                if (!data) return
                IslandState.wifiEnabled = data.trim() === "enabled"
            }
        }
    }
    
    Timer {
        interval: 3000
        running: true
        repeat: true
        onTriggered: networkProcess.running = true
    }

    // Bluetooth Status
    Process {
        id: bluetoothProcess
        command: ["sh", "-c", "bluetoothctl show | grep Powered | awk '{print $2}'"]
        running: true
        stdout: SplitParser {
            onRead: (data) => {
                if (!data) return
                IslandState.bluetoothEnabled = data.trim() === "yes"
            }
        }
    }
    
    Timer {
        interval: 3000
        running: true
        repeat: true
        onTriggered: bluetoothProcess.running = true
    }

    // Media Player Status (MPRIS)
    Process {
        id: mediaProcess
        command: ["sh", "-c", "playerctl status 2>/dev/null || echo 'stopped'"]
        running: true
        stdout: SplitParser {
            onRead: (data) => {
                if (!data) return
                IslandState.musicPlaying = data.trim().toLowerCase() === "playing"
            }
        }
    }
    
    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: mediaProcess.running = true
    }

    // ──────────────────────────────────────────────────────────────
    // GLOBAL KEYBOARD SHORTCUTS
    // ──────────────────────────────────────────────────────────────

    // Launcher toggle
    Shortcut {
        sequence: Constants.keyLauncher
        onActivated: IslandState.setMode(IslandState.Mode.Launcher)
    }

    // Control Center toggle
    Shortcut {
        sequence: Constants.keyControlCenter
        onActivated: IslandState.setMode(IslandState.Mode.ControlCenter)
    }

    // Power menu
    Shortcut {
        sequence: Constants.keyPowerMenu
        onActivated: IslandState.setMode(IslandState.Mode.Power)
    }

    // Settings
    Shortcut {
        sequence: Constants.keySettings
        onActivated: IslandState.setMode(IslandState.Mode.Settings)
    }

    // ──────────────────────────────────────────────────────────────
    // VOLUME/BRIGHTNESS DISPLAY OSD
    // ──────────────────────────────────────────────────────────────

    // Show volume OSD when volume changes
    Connections {
        target: IslandState
        function onVolumeLevelChanged() {
            IslandState.setMode(IslandState.Mode.Volume)
            autoCollapseTimer.restart()
        }
    }

    // Show brightness OSD when brightness changes
    Connections {
        target: IslandState
        function onBrightnessLevelChanged() {
            IslandState.setMode(IslandState.Mode.Brightness)
            autoCollapseTimer.restart()
        }
    }

    Timer {
        id: autoCollapseTimer
        interval: 2500
        onTriggered: {
            if (!IslandState.isPinned) {
                IslandState.resetToDefault()
            }
        }
    }

    // ──────────────────────────────────────────────────────────────
    // NOTIFICATION HANDLING
    // ──────────────────────────────────────────────────────────────

    NotificationService {
        id: notificationService
        onNotificationReceived: (notification) => {
            IslandState.currentNotification = notification
            IslandState.setMode(IslandState.Mode.Notification)
        }
    }
}
