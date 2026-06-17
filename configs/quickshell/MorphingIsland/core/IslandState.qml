pragma Singleton
import QtQuick

QtObject {
    // ──────────────────────────────────────────────────────────────────
    // STATE MANAGEMENT for MorphingIsland
    // ──────────────────────────────────────────────────────────────────

    enum Mode {
        Clock,
        Launcher,
        ControlCenter,
        Volume,
        Brightness,
        Notification,
        Power,
        Settings,
        Auth
    }

    property int currentMode: IslandState.Mode.Clock
    property bool isExpanded: false
    property bool isPinned: false

    // ──────────────────────────────────────────────────────────────────
    // NOTIFICATION STATE
    // ──────────────────────────────────────────────────────────────────
    property var currentNotification: null
    property bool hasNotification: false

    // ──────────────────────────────────────────────────────────────────
    // SYSTEM STATE
    // ──────────────────────────────────────────────────────────────────
    property real volumeLevel: 0.5
    property bool volumeMuted: false
    property real brightnessLevel: 0.8
    property bool wifiEnabled: false
    property bool bluetoothEnabled: false
    property bool musicPlaying: false

    // ──────────────────────────────────────────────────────────────────
    // AUTO-COLLAPSE TIMER
    // ──────────────────────────────────────────────────────────────────
    property int autoCollapseDelay: 3000

    function setMode(mode) {
        currentMode = mode
        isExpanded = (mode !== IslandState.Mode.Clock)
    }

    function resetToDefault() {
        currentMode = IslandState.Mode.Clock
        isExpanded = false
        isPinned = false
    }

    function togglePin() {
        isPinned = !isPinned
    }
}
