import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// VOLUME MODE - Shows volume level as morphing element
// Displays speaker icon + progress bar + percentage
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: volumeMode
    
    property real volumeLevel: 0.5  // 0.0 to 1.5
    property bool isMuted: false
    
    implicitWidth: contentRow.implicitWidth + 20
    implicitHeight: 40
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    RowLayout {
        id: contentRow
        anchors.centerIn: parent
        spacing: Constants.spacing
        
        // Volume icon (changes based on level)
        Item {
            Layout.preferredWidth: Constants.iconSize
            Layout.preferredHeight: Constants.iconSize
            
            Text {
                anchors.centerIn: parent
                font.pixelSize: Constants.iconSize
                color: volumeMode.isMuted ? Constants.accentRed : Constants.accentBlue
                
                text: {
                    if (volumeMode.isMuted) return "🔇"
                    if (volumeMode.volumeLevel < 0.3) return "🔈"
                    if (volumeMode.volumeLevel < 0.7) return "🔉"
                    return "🔊"
                }
                
                Behavior on text {
                    ScriptAction {
                        script: parent.scale = 0.8
                    }
                }
            }
        }
        
        // Volume bar
        Rectangle {
            Layout.preferredWidth: 180
            Layout.preferredHeight: 6
            
            color: Constants.bgOverlay
            radius: 3
            
            Rectangle {
                width: parent.width * Math.min(volumeMode.volumeLevel, 1.0)
                height: parent.height
                color: volumeMode.isMuted ? Constants.accentRed : Constants.accentBlue
                radius: 3
                
                Behavior on width {
                    SpringAnimation {
                        duration: 200
                    }
                }
            }
        }
        
        // Percentage text
        Text {
            Layout.preferredWidth: 40
            color: Constants.text
            font.family: "Google Sans"
            font.pixelSize: 13
            font.weight: Font.Medium
            text: Math.round(volumeMode.volumeLevel * 100) + "%"
        }
    }
    
    // Auto-collapse timer
    Timer {
        id: autoCollapseTimer
        interval: Constants.autoCollapseDelay
        running: false
        repeat: false
        
        onTriggered: {
            IslandState.setMode(IslandState.Mode.Clock)
        }
    }
    
    onVolumeDataChanged: {
        autoCollapseTimer.restart()
    }
}
