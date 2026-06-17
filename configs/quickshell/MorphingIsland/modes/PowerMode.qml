import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// POWER MENU MODE - System power controls
// Lock, suspend, logout, reboot, poweroff
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: powerMode
    
    implicitWidth: contentRow.implicitWidth + 24
    implicitHeight: 60
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    property var actionStates: ({})  // Track which action needs confirmation
    
    RowLayout {
        id: contentRow
        anchors.centerIn: parent
        spacing: Constants.spacingMd
        
        // Lock button
        PowerButton {
            icon: Icons.lock
            label: "Lock"
            destructive: false
            onClicked: {
                // Execute lock command
                IslandState.resetToDefault()
            }
        }
        
        // Suspend button
        PowerButton {
            icon: Icons.pause
            label: "Sleep"
            destructive: false
            onClicked: {
                // Execute suspend command
                IslandState.resetToDefault()
            }
        }
        
        // Reboot button (destructive)
        PowerButton {
            icon: "🔄"
            label: "Reboot"
            destructive: true
            confirmRequired: true
            onClicked: {
                if (!powerMode.actionStates["reboot"]) {
                    powerMode.actionStates = { ...powerMode.actionStates, reboot: true }
                } else {
                    // Execute reboot
                    powerMode.actionStates = { ...powerMode.actionStates, reboot: false }
                }
            }
            onCancelled: {
                powerMode.actionStates = { ...powerMode.actionStates, reboot: false }
            }
        }
        
        // Power off button (destructive)
        PowerButton {
            icon: Icons.power
            label: "Power"
            destructive: true
            confirmRequired: true
            onClicked: {
                if (!powerMode.actionStates["poweroff"]) {
                    powerMode.actionStates = { ...powerMode.actionStates, poweroff: true }
                } else {
                    // Execute poweroff
                    powerMode.actionStates = { ...powerMode.actionStates, poweroff: false }
                }
            }
            onCancelled: {
                powerMode.actionStates = { ...powerMode.actionStates, poweroff: false }
            }
        }
    }
}

// ──────────────────────────────────────────────────────────────────
// POWER BUTTON COMPONENT
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: powerButton
    
    property string icon: ""
    property string label: ""
    property bool destructive: false
    property bool confirmRequired: false
    property bool needsConfirm: false
    
    signal clicked()
    signal cancelled()
    
    implicitWidth: 70
    implicitHeight: 52
    
    color: needsConfirm 
        ? Constants.accentRed 
        : (destructive ? Constants.bgOverlay : Constants.accentGreen)
    radius: Constants.borderRadiusMd
    
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 4
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: powerButton.icon
            font.pixelSize: 20
        }
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: powerButton.needsConfirm ? "Confirm?" : powerButton.label
            color: Constants.text
            font.pixelSize: 11
            font.weight: Font.Medium
        }
    }
    
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            if (powerButton.confirmRequired) {
                if (powerButton.needsConfirm) {
                    powerButton.clicked()
                    powerButton.needsConfirm = false
                } else {
                    powerButton.needsConfirm = true
                    Timer {
                        interval: 3000
                        running: powerButton.needsConfirm
                        onTriggered: powerButton.needsConfirm = false
                    }
                }
            } else {
                powerButton.clicked()
            }
        }
    }
}
