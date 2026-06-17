import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// QUICK TOGGLE - Reusable toggle button for control center
// Split tap target: icon toggles, rest shows details
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: quickToggle
    
    property string icon: ""
    property string label: ""
    property bool enabled: false
    property color accentColor: Constants.accentGreen
    
    signal toggled()
    signal detailClicked()
    
    implicitWidth: 100
    implicitHeight: 100
    
    color: Constants.bgOverlay
    radius: Constants.borderRadiusMd
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8
        
        // Icon area
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 44
            Layout.preferredHeight: 44
            
            color: quickToggle.enabled ? quickToggle.accentColor : Constants.bgBase
            radius: Constants.borderRadiusSm
            
            Text {
                anchors.centerIn: parent
                text: quickToggle.icon
                font.pixelSize: 22
            }
            
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: quickToggle.toggled()
            }
        }
        
        // Label
        Text {
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            text: quickToggle.label
            color: Constants.text
            font.family: "Google Sans"
            font.pixelSize: 12
            font.weight: Font.Medium
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
        
        Item { Layout.fillHeight: true }
    }
    
    // Click area for details
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: quickToggle.detailClicked()
    }
}
