import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// NOTIFICATION MODE - Display and handle notifications
// Shows app icon + title + body
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: notificationMode
    
    implicitWidth: 360
    implicitHeight: 80
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    property var notification: ({})
    property bool isCritical: false
    property real dismissCountdown: 0
    property real dismissDelay: 5000
    
    // Auto-dismiss timer
    Timer {
        id: dismissTimer
        interval: 100
        running: notificationMode.dismissCountdown > 0
        repeat: true
        
        onTriggered: {
            notificationMode.dismissCountdown -= interval
            if (notificationMode.dismissCountdown <= 0) {
                running = false
                IslandState.resetToDefault()
            }
        }
    }
    
    onNotificationChanged: {
        notificationMode.dismissCountdown = notificationMode.dismissDelay
    }
    
    onMouseEntered: {
        dismissTimer.running = false
    }
    
    onMouseExited: {
        dismissTimer.running = true
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: Constants.spacing
        
        // App icon or avatar
        Rectangle {
            Layout.preferredWidth: 48
            Layout.preferredHeight: 48
            
            color: Constants.accentGreen
            radius: Constants.borderRadiusMd
            
            Text {
                anchors.centerIn: parent
                text: notificationMode.notification.appName?.charAt(0).toUpperCase() || "N"
                color: Constants.bgBase
                font.pixelSize: 20
                font.weight: Font.Bold
                font.family: "Google Sans"
            }
        }
        
        // Notification content
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 4
            
            Text {
                Layout.fillWidth: true
                text: notificationMode.notification.summary || "Notification"
                color: Constants.text
                font.pixelSize: 13
                font.weight: Font.Medium
                elide: Text.ElideRight
            }
            
            Text {
                Layout.fillWidth: true
                Layout.fillHeight: true
                text: notificationMode.notification.body || ""
                color: Constants.textMuted
                font.pixelSize: 11
                elide: Text.ElideRight
                wrapMode: Text.Wrap
            }
        }
        
        // Dismiss countdown indicator
        Rectangle {
            Layout.preferredWidth: 3
            Layout.fillHeight: true
            
            color: notificationMode.isCritical ? Constants.accentRed : Constants.accentGreen
            radius: 2
            
            Rectangle {
                width: parent.width
                height: parent.height * (1 - notificationMode.dismissCountdown / notificationMode.dismissDelay)
                anchors.bottom: parent.bottom
                color: parent.color
                
                Behavior on height {
                    NumberAnimation {
                        duration: 100
                    }
                }
            }
        }
    }
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onEntered: {
            dismissTimer.running = false
        }
        
        onExited: {
            dismissTimer.running = true
        }
        
        onClicked: {
            IslandState.resetToDefault()
        }
    }
}
