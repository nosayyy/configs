import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// CONTROL CENTER MODE - System settings panel
// Quick toggles, sliders, media controls, theme switcher
// Nested views with smooth transitions
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: controlCenterMode
    
    implicitWidth: 360
    implicitHeight: mainStack.implicitHeight + 24
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    property real volumeLevel: 0.5
    property bool volumeMuted: false
    property real brightnessLevel: 0.8
    property bool wifiEnabled: false
    property bool bluetoothEnabled: false
    property bool nightLightEnabled: false
    property string currentTheme: "Catppuccin Mocha"
    
    // Sub-view state
    enum SubView {
        Main,
        WiFi,
        Bluetooth,
        Audio,
        Themes
    }
    property int activeSubView: ControlCenterMode.SubView.Main
    
    StackLayout {
        id: mainStack
        anchors.fill: parent
        anchors.margins: 12
        
        currentIndex: controlCenterMode.activeSubView
        
        implicitHeight: itemAt(currentIndex)?.implicitHeight ?? 0
        
        // ────────────────────────────────────────────────────────────
        // MAIN VIEW
        // ────────────────────────────────────────────────────────────
        ColumnLayout {
            spacing: Constants.spacing
            
            // Quick toggles row
            RowLayout {
                Layout.fillWidth: true
                spacing: Constants.spacingMd
                
                // WiFi toggle
                QuickToggle {
                    icon: Icons.wifi
                    label: "WiFi"
                    enabled: controlCenterMode.wifiEnabled
                    onToggled: controlCenterMode.wifiEnabled = !controlCenterMode.wifiEnabled
                    onDetailClicked: controlCenterMode.activeSubView = ControlCenterMode.SubView.WiFi
                }
                
                // Bluetooth toggle
                QuickToggle {
                    icon: Icons.bluetooth
                    label: "Bluetooth"
                    enabled: controlCenterMode.bluetoothEnabled
                    onToggled: controlCenterMode.bluetoothEnabled = !controlCenterMode.bluetoothEnabled
                    onDetailClicked: controlCenterMode.activeSubView = ControlCenterMode.SubView.Bluetooth
                }
                
                // Night light toggle
                QuickToggle {
                    icon: Icons.sun
                    label: "Night"
                    enabled: controlCenterMode.nightLightEnabled
                    onToggled: controlCenterMode.nightLightEnabled = !controlCenterMode.nightLightEnabled
                }
            }
            
            // Volume slider
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                
                RowLayout {
                    Text {
                        text: "Volume"
                        color: Constants.text
                        font.pixelSize: 12
                        font.weight: Font.Medium
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: Math.round(controlCenterMode.volumeLevel * 100) + "%"
                        color: Constants.textMuted
                        font.pixelSize: 12
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 4
                    
                    color: Constants.bgOverlay
                    radius: 2
                    
                    Rectangle {
                        width: parent.width * controlCenterMode.volumeLevel
                        height: parent.height
                        color: Constants.accentBlue
                        radius: 2
                        
                        Behavior on width {
                            SpringAnimation { duration: 200 }
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: (mouse) => {
                            controlCenterMode.volumeLevel = Math.max(0, Math.min(1, mouse.x / width))
                        }
                    }
                }
            }
            
            // Brightness slider
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                
                RowLayout {
                    Text {
                        text: "Brightness"
                        color: Constants.text
                        font.pixelSize: 12
                        font.weight: Font.Medium
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: Math.round(controlCenterMode.brightnessLevel * 100) + "%"
                        color: Constants.textMuted
                        font.pixelSize: 12
                    }
                }
                
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 4
                    
                    color: Constants.bgOverlay
                    radius: 2
                    
                    Rectangle {
                        width: parent.width * controlCenterMode.brightnessLevel
                        height: parent.height
                        color: Constants.accentYellow
                        radius: 2
                        
                        Behavior on width {
                            SpringAnimation { duration: 200 }
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        onClicked: (mouse) => {
                            controlCenterMode.brightnessLevel = Math.max(0, Math.min(1, mouse.x / width))
                        }
                    }
                }
            }
            
            // Theme indicator
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 44
                
                color: Constants.bgOverlay
                radius: Constants.borderRadiusSm
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: Constants.spacingMd
                    
                    Text {
                        text: "Theme"
                        color: Constants.text
                        font.pixelSize: 12
                        font.weight: Font.Medium
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Text {
                        text: controlCenterMode.currentTheme
                        color: Constants.accentGreen
                        font.pixelSize: 12
                        font.family: "Google Sans"
                    }
                    
                    Image {
                        Layout.preferredWidth: 16
                        Layout.preferredHeight: 16
                        source: Icons.createSvg(Icons.chevronRight, Constants.accentGreen, 16)
                    }
                }
                
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: controlCenterMode.activeSubView = ControlCenterMode.SubView.Themes
                }
            }
        }
        
        // ────────────────────────────────────────────────────────────
        // WiFi SUB-VIEW
        // ────────────────────────────────────────────────────────────
        ColumnLayout {
            spacing: Constants.spacing
            
            RowLayout {
                spacing: Constants.spacingMd
                Layout.fillWidth: true
                
                Image {
                    Layout.preferredWidth: 16
                    Layout.preferredHeight: 16
                    source: Icons.createSvg(Icons.chevronRight, Constants.textMuted, 16)
                    rotation: 180
                }
                
                Text {
                    text: "Available Networks"
                    color: Constants.text
                    font.pixelSize: 13
                    font.weight: Font.Medium
                    Layout.fillWidth: true
                }
                
                MouseArea {
                    implicitWidth: 32
                    implicitHeight: 32
                    cursorShape: Qt.PointingHandCursor
                    onClicked: controlCenterMode.activeSubView = ControlCenterMode.SubView.Main
                }
            }
            
            Item { Layout.fillHeight: true }
            
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "No networks available"
                color: Constants.textMuted
                font.pixelSize: 12
            }
        }
        
        // ────────────────────────────────────────────────────────────
        // THEMES SUB-VIEW  
        // ────────────────────────────────────────────────────────────
        ColumnLayout {
            spacing: Constants.spacing
            
            RowLayout {
                spacing: Constants.spacingMd
                Layout.fillWidth: true
                
                Image {
                    Layout.preferredWidth: 16
                    Layout.preferredHeight: 16
                    source: Icons.createSvg(Icons.chevronRight, Constants.textMuted, 16)
                    rotation: 180
                }
                
                Text {
                    text: "Color Schemes"
                    color: Constants.text
                    font.pixelSize: 13
                    font.weight: Font.Medium
                    Layout.fillWidth: true
                }
                
                MouseArea {
                    implicitWidth: 32
                    implicitHeight: 32
                    cursorShape: Qt.PointingHandCursor
                    onClicked: controlCenterMode.activeSubView = ControlCenterMode.SubView.Main
                }
            }
            
            Flow {
                Layout.fillWidth: true
                spacing: Constants.spacing
                
                Repeater {
                    model: ["Catppuccin", "Dracula", "Gruvbox", "Nord", "One Dark", "Solarized"]
                    
                    Rectangle {
                        width: (controlCenterMode.width - 36 - 12) / 2
                        height: 50
                        
                        color: Constants.bgOverlay
                        radius: Constants.borderRadiusSm
                        
                        border.width: modelData === controlCenterMode.currentTheme ? 2 : 0
                        border.color: Constants.accentGreen
                        
                        Text {
                            anchors.centerIn: parent
                            text: modelData
                            color: Constants.text
                            font.pixelSize: 11
                            font.weight: Font.Medium
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: controlCenterMode.currentTheme = modelData
                        }
                    }
                }
            }
        }
    }
}
