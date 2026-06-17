import Quickshell
import Quickshell.Wayland
import Quickshell.Io
import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// MORPHING ISLAND - Main component
// Handles mode transitions, animations, state management
// ──────────────────────────────────────────────────────────────────

PanelWindow {
    id: island
    
    anchors.top: true
    anchors.horizontalCenter: true
    
    width: currentModeComponent?.implicitWidth ?? Constants.islandMinWidth
    height: currentModeComponent?.implicitHeight ?? Constants.islandMinHeight
    
    color: "transparent"
    WlrLayershell.namespace: "morphing-island"
    WlrLayershell.layer: WlrLayer.Top
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.OnDemand
    
    // Animation behavior
    Behavior on width {
        SpringAnimation {
            duration: Constants.animDurationMid
            easing.type: Easing.OutCubic
        }
    }
    
    Behavior on height {
        SpringAnimation {
            duration: Constants.animDurationMid
            easing.type: Easing.OutCubic
        }
    }
    
    // Margin from screen edge
    WlrLayershell.margins.top: 20
    
    // ──────────────────────────────────────────────────────────────
    // STATE MANAGEMENT
    // ──────────────────────────────────────────────────────────────
    
    property var currentModeComponent: clockModeComponent
    property int currentMode: IslandState.Mode.Clock
    property bool isExpanded: false
    
    // Auto-collapse timer (except for pinned island)
    Timer {
        id: autoCollapseTimer
        interval: Constants.autoCollapseDelay
        running: false
        repeat: false
        
        onTriggered: {
            if (!IslandState.isPinned) {
                resetToDefault()
            }
        }
    }
    
    // ──────────────────────────────────────────────────────────────
    // MODE SWITCHING LOGIC
    // ──────────────────────────────────────────────────────────────
    
    Connections {
        target: IslandState
        
        function onCurrentModeChanged() {
            island.switchMode(IslandState.currentMode)
        }
        
        function onIsExpandedChanged() {
            island.isExpanded = IslandState.isExpanded
            if (!IslandState.isPinned) {
                autoCollapseTimer.restart()
            }
        }
    }
    
    function switchMode(mode) {
        island.currentMode = mode
        
        switch (mode) {
            case IslandState.Mode.Clock:
                currentModeComponent = clockModeComponent
                break
            case IslandState.Mode.Launcher:
                currentModeComponent = launcherModeComponent
                break
            case IslandState.Mode.ControlCenter:
                currentModeComponent = controlCenterModeComponent
                break
            case IslandState.Mode.Volume:
                currentModeComponent = volumeModeComponent
                break
            case IslandState.Mode.Brightness:
                currentModeComponent = brightnessModeComponent
                break
            case IslandState.Mode.Notification:
                currentModeComponent = notificationModeComponent
                break
            case IslandState.Mode.Power:
                currentModeComponent = powerModeComponent
                break
            case IslandState.Mode.Settings:
                currentModeComponent = settingsModeComponent
                break
            default:
                currentModeComponent = clockModeComponent
        }
        
        autoCollapseTimer.restart()
    }
    
    function resetToDefault() {
        IslandState.resetToDefault()
        autoCollapseTimer.stop()
    }
    
    // ──────────────────────────────────────────────────────────────
    // MAIN CONTENT
    // ──────────────────────────────────────────────────────────────
    
    Rectangle {
        anchors.fill: parent
        color: Constants.bgSurface
        radius: Constants.borderRadius
        
        // Subtle shadow
        layer.enabled: true
        layer.effect: DropShadow {
            transparentBorder: true
            horizontalOffset: 0
            verticalOffset: 4
            radius: 12
            samples: 16
            color: "#00000044"
        }
        
        // Mode content
        Loader {
            id: modeLoader
            anchors.fill: parent
            
            sourceComponent: island.currentModeComponent
            
            Behavior on opacity {
                NumberAnimation {
                    duration: Constants.animDurationFast
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
    
    // ──────────────────────────────────────────────────────────────
    // MODE COMPONENTS (Lazy-loaded)
    // ──────────────────────────────────────────────────────────────
    
    Component {
        id: clockModeComponent
        ClockMode {
            musicPlaying: IslandState.musicPlaying
        }
    }
    
    Component {
        id: launcherModeComponent
        LauncherMode {}
    }
    
    Component {
        id: controlCenterModeComponent
        ControlCenterMode {}
    }
    
    Component {
        id: volumeModeComponent
        VolumeMode {
            volumeLevel: IslandState.volumeLevel
            isMuted: IslandState.volumeMuted
        }
    }
    
    Component {
        id: brightnessModeComponent
        BrightnessMode {
            brightnessLevel: IslandState.brightnessLevel
        }
    }
    
    Component {
        id: notificationModeComponent
        NotificationMode {
            notification: IslandState.currentNotification
        }
    }
    
    Component {
        id: powerModeComponent
        PowerMode {}
    }
    
    Component {
        id: settingsModeComponent
        SettingsMode {}
    }
    
    // ──────────────────────────────────────────────────────────────
    // KEYBOARD SHORTCUTS
    // ──────────────────────────────────────────────────────────────
    
    Shortcut {
        sequence: Constants.keyLauncher
        onActivated: IslandState.setMode(IslandState.Mode.Launcher)
    }
    
    Shortcut {
        sequence: Constants.keyControlCenter
        onActivated: IslandState.setMode(IslandState.Mode.ControlCenter)
    }
    
    Shortcut {
        sequence: Constants.keyPowerMenu
        onActivated: IslandState.setMode(IslandState.Mode.Power)
    }
    
    Shortcut {
        sequence: Constants.keySettings
        onActivated: IslandState.setMode(IslandState.Mode.Settings)
    }
    
    Shortcut {
        sequence: Constants.keyThemeSwitcher
        onActivated: IslandState.setMode(IslandState.Mode.Settings)
    }
    
    // Click handler for pin/unpin
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        
        onClicked: {
            if (island.currentMode === IslandState.Mode.Clock) {
                IslandState.togglePin()
            }
        }
    }
    
    // Ensure component is initially set
    Component.onCompleted: {
        switchMode(IslandState.Mode.Clock)
    }
}
