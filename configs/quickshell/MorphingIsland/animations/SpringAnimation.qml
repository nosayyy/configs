import QtQuick

// Critically damped spring animation
// Creates smooth, physical motion without overshoot
NumberAnimation {
    property real damping: 0.85
    property real stiffness: 200
    property real mass: 1.0

    duration: {
        // Calculate duration based on spring parameters
        var naturalFreq = Math.sqrt(stiffness / mass)
        return Math.max(250, Math.min(500, 1000 / naturalFreq))
    }

    easing.type: Easing.OutCubic
}

/* 
   SPRING PHYSICS EXPLANATION:
   
   A critically damped spring has a damping ratio = 1.0
   This means:
   - No oscillation (no "bounce")
   - Settles fastest without overshooting
   - Feels deliberate and fast
   
   Formula: damping ratio = c / (2 * sqrt(k * m))
   where:
     c = damping coefficient (0.85 for responsive feel)
     k = spring stiffness (200 for quick settlement)
     m = mass (1.0 for unit mass)
*/
