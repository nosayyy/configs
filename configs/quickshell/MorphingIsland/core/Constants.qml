pragma Singleton
import QtQuick

QtObject {
    // ──────────────────────────────────────────────────────────────────
    // COLORS - Catppuccin Mocha
    // ──────────────────────────────────────────────────────────────────
    readonly property color bgBase:     "#1e1e2e"  // Background base
    readonly property color bgSurface:  "#313244"  // Surface/cards
    readonly property color bgOverlay:  "#45475a"  // Overlays
    readonly property color text:       "#cdd6f4"  // Text primary
    readonly property color textMuted:  "#a6adc8"  // Text muted
    readonly property color accentGreen:    "#a6e3a1"  // Primary accent
    readonly property color accentBlue:     "#89b4fa"  // Secondary accent
    readonly property color accentRed:      "#f38ba8"  // Destructive
    readonly property color accentYellow:   "#f9e2af"  // Warning
    readonly property color accentPurple:   "#cba6f7"  // Info
    readonly property color borderColor:    "#45475a"  // Borders

    // ──────────────────────────────────────────────────────────────────
    // SIZING & SPACING
    // ──────────────────────────────────────────────────────────────────
    readonly property int borderRadius: 16
    readonly property int borderRadiusMd: 12
    readonly property int borderRadiusSm: 8

    readonly property int spacing: 12
    readonly property int spacingMd: 8
    readonly property int spacingSm: 4

    readonly property int iconSize: 20
    readonly property int iconSizeMd: 16
    readonly property int iconSizeSm: 12

    // ──────────────────────────────────────────────────────────────────
    // ISLAND DIMENSIONS
    // ──────────────────────────────────────────────────────────────────
    readonly property int islandMinWidth: 48
    readonly property int islandMinHeight: 48
    readonly property int islandMaxWidth: 400
    readonly property int islandMaxHeight: 500

    // ──────────────────────────────────────────────────────────────────
    // ANIMATION TIMINGS
    // ──────────────────────────────────────────────────────────────────
    readonly property int animDurationFast: 150
    readonly property int animDurationMid: 300
    readonly property int animDurationSlow: 500

    // Spring physics constants (critically damped)
    readonly property real springMass: 1.0
    readonly property real springDamping: 0.85
    readonly property real springStiffness: 200

    // ──────────────────────────────────────────────────────────────────
    // KEYBOARD SHORTCUTS
    // ──────────────────────────────────────────────────────────────────
    readonly property string keyLauncher:     "Alt+D"
    readonly property string keyControlCenter: "Alt+A"
    readonly property string keyPowerMenu:    "Ctrl+Alt+Delete"
    readonly property string keySettings:     "Alt+,"
    readonly property string keyThemeSwitcher: "Alt+Shift+T"
}
