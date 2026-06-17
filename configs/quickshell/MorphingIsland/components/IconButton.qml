import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// ICON BUTTON - Reusable icon button with hover effects
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: iconButton
    
    property string icon: ""
    property string label: ""
    property color iconColor: Constants.text
    property color hoverColor: Constants.accentGreen
    
    signal clicked()
    
    implicitWidth: 40
    implicitHeight: 40
    
    color: iconButton.containsMouse ? hoverColor : "transparent"
    radius: Constants.borderRadiusSm
    
    opacity: 0.8
    
    Behavior on color {
        ColorAnimation { duration: Constants.animDurationFast }
    }
    
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 2
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: iconButton.icon
            font.pixelSize: Constants.iconSize
            color: iconButton.iconColor
        }
        
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: iconButton.label
            font.pixelSize: 8
            color: iconButton.iconColor
            visible: label !== ""
        }
    }
    
    property bool containsMouse: hoverArea.containsMouse
    
    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onClicked: iconButton.clicked()
    }
}
