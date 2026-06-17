pragma Singleton
import QtQuick

// Hand-drawn custom SVG icons (no icon fonts!)
// All icons are vector shapes that respond to theming

QtObject {
    // ──────────────────────────────────────────────────────────────────
    // UTILITY FUNCTIONS
    // ──────────────────────────────────────────────────────────────────
    
    function createSvg(paths, color, size) {
        return "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='" + (size||24) + 
               "' height='" + (size||24) + "' viewBox='0 0 24 24' fill='none' stroke='" + color + 
               "' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>" + paths + "</svg>"
    }

    // ──────────────────────────────────────────────────────────────────
    // ICON PATHS
    // ──────────────────────────────────────────────────────────────────
    
    readonly property string clock:       "<circle cx='12' cy='12' r='9'/><polyline points='12 6 12 12 16 14'/>"
    readonly property string search:      "<circle cx='11' cy='11' r='8'/><path d='m21 21-4.35-4.35'/>"
    readonly property string settings:    "<path d='M12 1v6m0 6v6'/><path d='M4.22 4.22l4.24 4.24m5.08 0l4.24-4.24'/><path d='M1 12h6m6 0h6'/><path d='M4.22 19.78l4.24-4.24m5.08 0l4.24 4.24'/>"
    readonly property string wifi:        "<path d='M5 12.55a11 11 0 0 1 14.08 0'/><path d='M1.42 9a16 16 0 0 1 21.16 0'/><path d='M8.53 16.11a6 6 0 0 1 6.94 0'/><circle cx='12' cy='20' r='1'/>"
    readonly property string bluetooth:   "<polyline points='6.5 6.5 17.5 17.5 12 23 12 1 17.5 6.5 6.5 17.5'/>"
    readonly property string volume3:     "<path d='M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z'/><path d='M16 9a5 5 0 0 1 0 6'/><path d='M19.364 18.364a9 9 0 0 0 0-12.728'/>"
    readonly property string volumeMute:  "<path d='M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z'/><line x1='22' x2='16' y1='9' y2='15'/><line x1='16' x2='22' y1='9' y2='15'/>"
    readonly property string sun:         "<circle cx='12' cy='12' r='5'/><line x1='12' y1='1' x2='12' y2='3'/><line x1='12' y1='21' x2='12' y2='23'/><line x1='4.22' y1='4.22' x2='5.64' y2='5.64'/><line x1='18.36' y1='18.36' x2='19.78' y2='19.78'/><line x1='1' y1='12' x2='3' y2='12'/><line x1='21' y1='12' x2='23' y2='12'/><line x1='4.22' y1='19.78' x2='5.64' y2='18.36'/><line x1='18.36' y1='5.64' x2='19.78' y2='4.22'/>"
    readonly property string battery:     "<rect x='1' y='6' width='18' height='12' rx='2' ry='2'/><line x1='23' y1='13' x2='20' y2='13'/>"
    readonly property string play:        "<polygon points='6 3 20 12 6 21 6 3'/>"
    readonly property string pause:       "<rect x='6' y='4' width='4' height='16' rx='1'/><rect x='14' y='4' width='4' height='16' rx='1'/>"
    readonly property string power:       "<path d='M12 2v10'/><path d='M18.4 6.6a9 9 0 1 1-12.77.04'/>"
    readonly property string lock:        "<rect x='3' y='11' width='18' height='11' rx='2' ry='2'/><path d='M7 11V7a5 5 0 0 1 10 0v4'/>"
    readonly property string menu:        "<line x1='8' y1='6' x2='21' y2='6'/><line x1='8' y1='12' x2='21' y2='12'/><line x1='8' y1='18' x2='21' y2='18'/>"
    readonly property string x:           "<line x1='18' y1='6' x2='6' y2='18'/><line x1='6' y1='6' x2='18' y2='18'/>"
    readonly property string check:       "<polyline points='20 6 9 17 4 12'/>"
    readonly property string chevronRight: "<polyline points='9 18 15 12 9 6'/>"
    readonly property string chevronDown: "<polyline points='6 9 12 15 18 9'/>"
}
