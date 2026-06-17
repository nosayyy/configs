pragma Singleton
import QtQuick

// ──────────────────────────────────────────────────────────────────
// SYSTEM STATS SERVICE
// Provides real-time system statistics via properties
// Monitored by shell processes and updated periodically
// ──────────────────────────────────────────────────────────────────

QtObject {
    id: systemStats
    
    // CPU metrics
    property int cpuPct: 0
    property int cpuTemp: 0
    
    // Memory metrics
    property int ramPct: 0
    
    // Storage metrics
    property int diskUsage: 0
    
    // Signals for external updates
    signal cpuPctChanged()
    signal cpuTempChanged()
    signal ramPctChanged()
    signal diskUsageChanged()
}
