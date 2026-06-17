import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// BRIGHTNESS MODE - Shows brightness level as morphing element
// Displays sun icon with animated rays + progress bar
// Auto-collapses after adjustment
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: brightnessMode
    
    property real brightnessLevel: 0.8  // 0.0 to 1.0
    
    implicitWidth: contentRow.implicitWidth + 20
    implicitHeight: 40
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    RowLayout {
        id: contentRow
        anchors.centerIn: parent
        spacing: Constants.spacing
        
        // Sun icon with animated rays
        Item {
            Layout.preferredWidth: Constants.iconSize
            Layout.preferredHeight: Constants.iconSize
            
            Canvas {
                anchors.fill: parent
                
                onPaint: {
                    var ctx = getContext("2d")
                    ctx.clearRect(0, 0, width, height)
                    
                    var centerX = width / 2
                    var centerY = height / 2
                    var radius = width / 3
                    var brightness = brightnessMode.brightnessLevel
                    
                    // Draw sun rays (brightness-dependent)
                    ctx.strokeStyle = Constants.accentYellow
                    ctx.lineWidth = 1.5
                    ctx.lineCap = "round"
                    
                    for (var i = 0; i < 8; i++) {
                        var angle = (i * Math.PI * 2 / 8)
                        var innerRadius = radius * 0.6
                        var outerRadius = radius * (0.8 + brightness * 0.4)
                        
                        ctx.beginPath()
                        ctx.moveTo(
                            centerX + Math.cos(angle) * innerRadius,
                            centerY + Math.sin(angle) * innerRadius
                        )
                        ctx.lineTo(
                            centerX + Math.cos(angle) * outerRadius,
                            centerY + Math.sin(angle) * outerRadius
                        )
                        ctx.stroke()
                    }
                    
                    // Draw sun circle
                    ctx.fillStyle = Constants.accentYellow
                    ctx.beginPath()
                    ctx.arc(centerX, centerY, radius * 0.5, 0, Math.PI * 2)
                    ctx.fill()
                }
                
                Connections {
                    target: brightnessMode
                    function onBrightnessLevelChanged() {
                        parent.requestPaint()
                    }
                }
            }
        }
        
        // Brightness bar
        Rectangle {
            Layout.preferredWidth: 180
            Layout.preferredHeight: 6
            
            color: Constants.bgOverlay
            radius: 3
            
            Rectangle {
                width: parent.width * brightnessMode.brightnessLevel
                height: parent.height
                color: Constants.accentYellow
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
            text: Math.round(brightnessMode.brightnessLevel * 100) + "%"
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
    
    onBrightnessLevelChanged: {
        autoCollapseTimer.restart()
    }
}
