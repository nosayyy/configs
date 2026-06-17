import QtQuick
import QtQuick.Controls.Basic

// ──────────────────────────────────────────────────────────────────
// CUSTOM SLIDER - Smooth, themed slider component
// Used in control center and settings
// ──────────────────────────────────────────────────────────────────

Slider {
    id: slider
    
    from: 0
    to: 100
    stepSize: 1
    
    implicitWidth: 200
    implicitHeight: 6
    
    background: Rectangle {
        x: slider.leftPadding
        y: slider.topPadding + slider.availableHeight / 2 - height / 2
        implicitWidth: 200
        implicitHeight: 6
        
        width: slider.availableWidth
        height: implicitHeight
        
        radius: 3
        color: Constants.bgOverlay
        
        Rectangle {
            width: slider.visualPosition * parent.width
            height: parent.height
            radius: 3
            color: Constants.accentGreen
            
            Behavior on width {
                NumberAnimation {
                    duration: 100
                    easing.type: Easing.OutCubic
                }
            }
        }
    }
    
    handle: Rectangle {
        x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
        y: slider.topPadding + slider.availableHeight / 2 - height / 2
        
        implicitWidth: 16
        implicitHeight: 16
        
        radius: 8
        color: Constants.accentGreen
        
        shadow: DropShadow {
            transparentBorder: true
            horizontalOffset: 0
            verticalOffset: 2
            radius: 4
            samples: 9
            color: "#00000033"
        }
        
        Behavior on x {
            NumberAnimation {
                duration: 100
                easing.type: Easing.OutCubic
            }
        }
    }
}
