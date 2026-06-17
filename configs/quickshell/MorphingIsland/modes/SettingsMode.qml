import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// SETTINGS MODE - Persistent UI configuration
// Adjust island height, font size, animation speed
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: settingsMode
    
    implicitWidth: 360
    implicitHeight: contentCol.implicitHeight + 24
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    property real islandHeight: 40
    property real fontSize: 14
    property real animationSpeed: 1.0
    
    ColumnLayout {
        id: contentCol
        anchors.fill: parent
        anchors.margins: 12
        spacing: Constants.spacing
        
        Text {
            text: "Island Settings"
            color: Constants.text
            font.pixelSize: 16
            font.weight: Font.Bold
            font.family: "Google Sans"
        }
        
        // Height setting
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            
            RowLayout {
                Text {
                    text: "Island Height"
                    color: Constants.text
                    font.pixelSize: 12
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: Math.round(settingsMode.islandHeight) + "px"
                    color: Constants.textMuted
                    font.pixelSize: 12
                }
            }
            
            Slider {
                Layout.fillWidth: true
                from: 32
                to: 64
                stepSize: 1
                value: settingsMode.islandHeight
                onMoved: settingsMode.islandHeight = value
            }
        }
        
        // Font size setting
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            
            RowLayout {
                Text {
                    text: "Font Size"
                    color: Constants.text
                    font.pixelSize: 12
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: Math.round(settingsMode.fontSize) + "px"
                    color: Constants.textMuted
                    font.pixelSize: 12
                }
            }
            
            Slider {
                Layout.fillWidth: true
                from: 10
                to: 18
                stepSize: 0.5
                value: settingsMode.fontSize
                onMoved: settingsMode.fontSize = value
            }
        }
        
        // Animation speed
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6
            
            RowLayout {
                Text {
                    text: "Animation Speed"
                    color: Constants.text
                    font.pixelSize: 12
                }
                Item { Layout.fillWidth: true }
                Text {
                    text: (settingsMode.animationSpeed * 100).toFixed(0) + "%"
                    color: Constants.textMuted
                    font.pixelSize: 12
                }
            }
            
            Slider {
                Layout.fillWidth: true
                from: 0.5
                to: 2.0
                stepSize: 0.1
                value: settingsMode.animationSpeed
                onMoved: settingsMode.animationSpeed = value
            }
        }
    }
}
