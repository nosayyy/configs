import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// LAUNCHER MODE - Application search and launch
// Keyboard-driven, fully focused, allows calculator/clipboard modes
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: launcherMode
    
    implicitWidth: 380
    implicitHeight: {
        var headerHeight = 56
        var itemHeight = 40
        var itemsToShow = Math.min(filteredApps.length, 6)
        return headerHeight + (itemsToShow * itemHeight) + 16
    }
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    property string searchText: ""
    property var allApps: []
    property var filteredApps: searchText.length > 0 
        ? allApps.filter(app => app.name.toLowerCase().includes(searchText.toLowerCase()))
        : []
    property int selectedIndex: 0
    
    // Mode types
    enum SearchMode {
        Apps,
        Calculator,
        Clipboard
    }
    property int searchMode: LauncherMode.SearchMode.Apps
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: Constants.spacing
        
        // Search input field
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            
            color: Constants.bgOverlay
            radius: Constants.borderRadiusMd
            
            TextInput {
                id: searchInput
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                
                verticalAlignment: TextInput.AlignVCenter
                font.family: "Google Sans"
                font.pixelSize: 14
                color: Constants.text
                
                onTextChanged: {
                    launcherMode.searchText = text
                    launcherMode.selectedIndex = 0
                    
                    // Detect mode switches
                    if (text.startsWith("=")) {
                        launcherMode.searchMode = LauncherMode.SearchMode.Calculator
                        launcherMode.searchText = text.substring(1)
                    } else if (text.startsWith(":")) {
                        launcherMode.searchMode = LauncherMode.SearchMode.Clipboard
                        launcherMode.searchText = text.substring(1)
                    } else {
                        launcherMode.searchMode = LauncherMode.SearchMode.Apps
                    }
                }
                
                Keys.onPressed: (event) => {
                    if (event.key === Qt.Key_Up) {
                        launcherMode.selectedIndex = Math.max(0, launcherMode.selectedIndex - 1)
                        event.accepted = true
                    } else if (event.key === Qt.Key_Down) {
                        launcherMode.selectedIndex = Math.min(launcherMode.filteredApps.length - 1, launcherMode.selectedIndex + 1)
                        event.accepted = true
                    } else if (event.key === Qt.Key_Return) {
                        if (launcherMode.selectedIndex >= 0 && launcherMode.selectedIndex < launcherMode.filteredApps.length) {
                            var app = launcherMode.filteredApps[launcherMode.selectedIndex]
                            // Launch app logic here
                            IslandState.resetToDefault()
                        }
                        event.accepted = true
                    } else if (event.key === Qt.Key_Escape) {
                        IslandState.resetToDefault()
                        event.accepted = true
                    }
                }
                
                Component.onCompleted: {
                    forceActiveFocus()
                }
            }
        }
        
        // Results list
        ListView {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(contentHeight, 240)
            
            model: launcherMode.filteredApps
            clip: true
            
            delegate: Rectangle {
                required property int index
                required property var modelData
                
                width: ListView.view.width
                height: 40
                
                color: launcherMode.selectedIndex === index ? Constants.accentGreen : "transparent"
                radius: Constants.borderRadiusSm
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: Constants.spacingMd
                    
                    Item {
                        Layout.preferredWidth: 24
                        Layout.preferredHeight: 24
                        
                        Image {
                            anchors.fill: parent
                            source: modelData.icon || ""
                            sourceSize: Qt.size(24, 24)
                            smooth: true
                        }
                    }
                    
                    Text {
                        Layout.fillWidth: true
                        text: modelData.name
                        color: launcherMode.selectedIndex === index ? Constants.bgBase : Constants.text
                        font.family: "Google Sans"
                        font.pixelSize: 12
                        font.weight: Font.Medium
                        elide: Text.ElideRight
                    }
                }
                
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        launcherMode.selectedIndex = index
                    }
                }
            }
        }
    }
}
