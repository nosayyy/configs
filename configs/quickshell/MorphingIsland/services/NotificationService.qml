import QtQuick

// ──────────────────────────────────────────────────────────────────
// NOTIFICATION SERVICE
// Listens for and dispatches system notifications
// ──────────────────────────────────────────────────────────────────

QtObject {
    id: notificationService
    
    // Properties for current notification
    property var currentNotification: ({})
    property bool notificationActive: false
    
    // Notification queue
    property var notificationQueue: []
    
    signal notificationReceived(var notification)
    signal notificationClosed()
    
    // Mock notification function for testing
    function showNotification(title, body, appName, appIcon, isCritical) {
        var notification = {
            id: Math.random(),
            summary: title,
            body: body,
            appName: appName || "App",
            appIcon: appIcon || "",
            critical: isCritical || false,
            timestamp: new Date()
        }
        
        currentNotification = notification
        notificationActive = true
        notificationReceived(notification)
        
        // Auto-dismiss after delay (unless critical)
        Timer {
            interval: isCritical ? 7000 : 5000
            running: true
            onTriggered: {
                notificationActive = false
                notificationClosed()
            }
        }
        
        return notification
    }
    
    // Queue notification for display
    function enqueueNotification(notification) {
        notificationQueue.push(notification)
        if (!notificationActive) {
            showNextNotification()
        }
    }
    
    // Display next notification in queue
    function showNextNotification() {
        if (notificationQueue.length > 0) {
            var notification = notificationQueue.shift()
            currentNotification = notification
            notificationActive = true
            notificationReceived(notification)
        }
    }
    
    // Clear all notifications
    function clearAll() {
        notificationQueue = []
        currentNotification = {}
        notificationActive = false
    }
}
