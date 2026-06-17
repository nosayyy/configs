import QtQuick
import QtQuick.Layouts

// ──────────────────────────────────────────────────────────────────
// CLOCK MODE - Default mode showing time
// The collapsed pill showing clock + optional EQ bars for music
// ──────────────────────────────────────────────────────────────────

Rectangle {
    id: clockMode
    
    property bool musicPlaying: false
    property int eqBarsCount: 3
    
    implicitWidth: contentRow.implicitWidth + 16
    implicitHeight: 40
    
    color: Constants.bgSurface
    radius: Constants.borderRadius
    
    // Smooth glow effect
    layer.enabled: true
    layer.effect: ShaderEffect {
        id: glowShader
        property color glowColor: Constants.accentGreen
        property real glowStrength: 0.3
        
        fragmentShader: "
            uniform sampler2D source;
            uniform vec4 glowColor;
            uniform float glowStrength;
            varying highp vec2 qt_TexCoord0;
            
            void main() {
                vec4 sourceColor = texture2D(source, qt_TexCoord0);
                gl_FragColor = mix(sourceColor, glowColor, glowStrength * 0.1);
            }
        "
    }
    
    RowLayout {
        id: contentRow
        anchors.centerIn: parent
        spacing: Constants.spacingMd
        
        // Time display
        Column {
            Layout.alignment: Qt.AlignVCenter
            spacing: 2
            
            Text {
                id: timeText
                color: Constants.text
                font.family: "Google Sans"
                font.pixelSize: 18
                font.weight: Font.Bold
                
                Timer {
                    interval: 1000
                    running: true
                    repeat: true
                    triggeredOnStart: true
                    
                    onTriggered: {
                        var now = new Date()
                        timeText.text = now.getHours().toString().padStart(2, '0') + ":" +
                                       now.getMinutes().toString().padStart(2, '0')
                    }
                }
            }
            
            Text {
                color: Constants.textMuted
                font.family: "Google Sans"
                font.pixelSize: 11
                opacity: 0.7
                
                Timer {
                    interval: 60000
                    running: true
                    repeat: true
                    triggeredOnStart: true
                    
                    onTriggered: {
                        var now = new Date()
                        var days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                        var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                        parent.text = days[now.getDay()] + " " + months[now.getMonth()] + " " + now.getDate()
                    }
                }
            }
        }
        
        // EQ Bars (visible when music playing)
        Row {
            Layout.alignment: Qt.AlignVCenter
            spacing: 3
            visible: clockMode.musicPlaying
            
            Repeater {
                model: clockMode.eqBarsCount
                
                Rectangle {
                    width: 3
                    height: 12 + Math.sin(index * 0.3 + Date.now() * 0.003) * 6
                    radius: 2
                    color: Constants.accentGreen
                    opacity: 0.8 + Math.sin(index * 0.4 + Date.now() * 0.004) * 0.2
                    
                    Behavior on height {
                        SpringAnimation {
                            duration: 100
                        }
                    }
                }
            }
            
            Timer {
                interval: 50
                running: clockMode.musicPlaying
                repeat: true
                onTriggered: parent.update()
            }
        }
    }
}
