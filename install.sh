#!/usr/bin/env bash
set -euo pipefail

# ──[ Configuration ]────────────────────────────────────────────────────────
REPO_ARG="${1:-}"
SESSION_MODE="${2:-}"
readonly CONFIG_NAME="qtile"
readonly CONFIG_DIR="$HOME/.config/${CONFIG_NAME}"
readonly LOG="/tmp/${CONFIG_NAME}-install.log"
readonly XSESSION="$HOME/.local/share/xsessions/${CONFIG_NAME}.desktop"
readonly WAYLAND_SESSION="$HOME/.local/share/wayland-sessions/${CONFIG_NAME}.desktop"
readonly DRY_RUN="${DRY_RUN:-0}"

usage() {
    cat <<EOF
Usage: ./install.sh [repo_path] [x11|wayland|auto]

Examples:
  ./install.sh
  ./install.sh /path/to/repo wayland
  DRY_RUN=1 ./install.sh . auto
EOF
}

# ──[ Colors ]────────────────────────────────────────────────────────────────
R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' C='\033[0;36m' N='\033[0m'

# ──[ Helpers ]───────────────────────────────────────────────────────────────
info()  { echo -e "${G}[+]${N} $*" | tee -a "$LOG"; }
warn()  { echo -e "${Y}[!]${N} $*" | tee -a "$LOG"; }
err()   { echo -e "${R}[✗]${N} $*" | tee -a "$LOG"; exit 1; }
ask()   { read -rp "$* [Y/n] " a; [[ "${a:-y}" =~ ^[Yy]$ ]]; }
cmd()   { command -v "$1" >/dev/null 2>&1; }
run_cmd() {
    if [ "$DRY_RUN" = "1" ]; then
        info "[dry-run] $*"
    else
        "$@"
    fi
}

# ──[ Pre-checks ]───────────────────────────────────────────────────────────
[ "$(id -u)" -eq 0 ] && err "Running as root is not allowed. Please use a regular user."
[ -z "$REPO_ARG" ] && REPO_ARG="$(pwd)"

if [ "$DRY_RUN" = "1" ]; then
    info "Dry-run mode enabled. No packages or system files will be modified."
else
    [ -d "$CONFIG_DIR" ] && {
        ask "Config $CONFIG_DIR already exists. Overwrite it?" || { info "Cancelled"; exit 0; }
    }
fi

# ──[ Environment detection ]───────────────────────────────────────────────
ESCAL=""
if [ "$DRY_RUN" != "1" ]; then
    for t in sudo doas; do
        if cmd "$t"; then
            ESCAL="$t"
            break
        fi
    done
    [ -z "$ESCAL" ] && err "sudo or doas is required."
fi

DISTRO=""
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO="${ID,,}"
else
    err "Could not detect the distribution."
fi

case "$DISTRO" in
    arch|manjaro|endeavouros)     PM="pacman" ;;
    debian|ubuntu|linuxmint|pop)  PM="apt"    ;;
    fedora|rhel|centos)           PM="dnf"    ;;
    opensuse*)                    PM="zypper" ;;
    *)                            PM="apt"    ;;
esac

info "Distribution: $DISTRO | Package manager: $PM | Privilege escalation: $ESCAL"

APT_UPDATED=0

install_pkgs() {
    local pkgs=("$@")
    if [ "$DRY_RUN" = "1" ]; then
        info "[dry-run] would install packages: ${pkgs[*]}"
        return
    fi

    case "$PM" in
        pacman) run_cmd "$ESCAL" pacman -S --noconfirm --needed "${pkgs[@]}" ;;
        apt)
            if [ "$APT_UPDATED" -eq 0 ]; then
                run_cmd "$ESCAL" apt update
                APT_UPDATED=1
            fi
            run_cmd "$ESCAL" apt install -y "${pkgs[@]}"
            ;;
        dnf) run_cmd "$ESCAL" dnf install -y "${pkgs[@]}" ;;
        zypper) run_cmd "$ESCAL" zypper install -y "${pkgs[@]}" ;;
    esac
}

install_pkgs_soft() {
    local pkgs=("$@")
    if [ "$DRY_RUN" = "1" ]; then
        info "[dry-run] would install optional packages: ${pkgs[*]}"
        return
    fi

    if ! case "$PM" in
        pacman) run_cmd "$ESCAL" pacman -S --noconfirm --needed "${pkgs[@]}" ;;
        apt)
            if [ "$APT_UPDATED" -eq 0 ]; then
                run_cmd "$ESCAL" apt update
                APT_UPDATED=1
            fi
            run_cmd "$ESCAL" apt install -y "${pkgs[@]}"
            ;;
        dnf) run_cmd "$ESCAL" dnf install -y "${pkgs[@]}" ;;
        zypper) run_cmd "$ESCAL" zypper install -y "${pkgs[@]}" ;;
    esac; then
        warn "Some optional packages could not be installed: ${pkgs[*]}"
    fi
}

install_python_pkg() {
    if [ "$DRY_RUN" = "1" ]; then
        info "[dry-run] would install Python package: $1"
    else
        python3 -m pip install --user "$1"
    fi
}

select_session_mode() {
    if [ -n "$SESSION_MODE" ]; then
        case "${SESSION_MODE,,}" in
            x11|x) SESSION_TYPE="x11" ;;
            wayland|w|wl) SESSION_TYPE="wayland" ;;
            auto|a) SESSION_TYPE="auto" ;;
            *) err "Unsupported session mode: $SESSION_MODE" ;;
        esac
        return
    fi

    if [ -n "${XDG_SESSION_TYPE:-}" ]; then
        case "${XDG_SESSION_TYPE,,}" in
            x11) SESSION_TYPE="x11" ; return ;;
            wayland) SESSION_TYPE="wayland" ; return ;;
        esac
    fi

    echo ""
    echo "Choose a session type:"
    echo "  [1] X11"
    echo "  [2] Wayland"
    echo "  [3] Auto"
    read -rp "Selection [1/2/3]: " choice
    case "$choice" in
        1|x11|X11) SESSION_TYPE="x11" ;;
        2|wayland|Wayland|w|W) SESSION_TYPE="wayland" ;;
        3|auto|Auto|a|A|"") SESSION_TYPE="auto" ;;
        *) err "Unsupported selection" ;;
    esac
}

resolve_session_type() {
    case "$SESSION_TYPE" in
        x11|wayland) ;;
        auto)
            if [ -n "${WAYLAND_DISPLAY:-}" ] || [ "${XDG_SESSION_TYPE:-}" = "wayland" ]; then
                SESSION_TYPE="wayland"
            elif [ -n "${DISPLAY:-}" ] || [ "${XDG_SESSION_TYPE:-}" = "x11" ]; then
                SESSION_TYPE="x11"
            else
                warn "No active display detected; defaulting to X11"
                SESSION_TYPE="x11"
            fi
            ;;
    esac
}

select_session_mode
resolve_session_type
info "Selected session: $SESSION_TYPE"

case "$PM" in
    pacman)
        install_pkgs git python python-pip python-cairo python-dbus python-tk qtile
        install_pkgs xorg-server xorg-xinit xterm
        if [ "$SESSION_TYPE" = "wayland" ]; then
            install_pkgs_soft wlroots wayland-protocols
        fi
        ;;
    apt)
        install_pkgs git python3 python3-pip python3-cairo python3-dbus python3-tk libpangocairo-1.0-0
        if apt-cache show qtile >/dev/null 2>&1; then
            install_pkgs qtile
        else
            warn "Qtile was not found in APT; installing via pip..."
            install_python_pkg qtile
        fi
        install_pkgs xorg xinit xterm
        if [ "$SESSION_TYPE" = "wayland" ]; then
            install_pkgs_soft wayland-protocols libwlroots-dev
        fi
        ;;
    dnf)
        install_pkgs git python3 python3-pip cairo-devel pango-devel python3-tk
        warn "Qtile was not found in the repository; installing via pip..."
        install_python_pkg qtile
        install_pkgs xorg-x11-server-Xorg xorg-x11-xinit xterm
        if [ "$SESSION_TYPE" = "wayland" ]; then
            install_pkgs_soft wlroots wayland-protocols
        fi
        ;;
    zypper)
        install_pkgs git python3 python3-pip python3-tk
        warn "Qtile was not found in the repository; installing via pip..."
        install_python_pkg qtile
        install_pkgs xorg-x11-server xinit xterm
        if [ "$SESSION_TYPE" = "wayland" ]; then
            install_pkgs_soft wlroots wayland-protocols
        fi
        ;;
esac

export PATH="$HOME/.local/bin:$PATH"

# ──[ Backup ]──────────────────────────────────────────────────────────────
if [ -d "$CONFIG_DIR" ]; then
    if [ "$DRY_RUN" = "1" ]; then
        info "[dry-run] would backup existing config from $CONFIG_DIR"
    else
        BACKUP="${CONFIG_DIR}.bak.$(date +%s)"
        mv "$CONFIG_DIR" "$BACKUP"
        info "Backup created: $BACKUP"
    fi
fi
mkdir -p "$CONFIG_DIR"

# ──[ Clone/find config ]───────────────────────────────────────────────────
TMP=""
if [ -d "$REPO_ARG" ]; then
    info "Using local path: $REPO_ARG"
    SRC="$REPO_ARG"
else
    info "Cloning $REPO_ARG ..."
    TMP="$(mktemp -d)"
    git clone --depth 1 "$REPO_ARG" "$TMP"
    SRC="$TMP"
fi

SOURCE_DIR=""
if [ -d "$SRC/rice" ] && [ -f "$SRC/rice/config.py" ]; then
    SOURCE_DIR="$SRC/rice"
elif [ -d "$SRC/configs/$CONFIG_NAME" ]; then
    SOURCE_DIR="$SRC/configs/$CONFIG_NAME"
elif [ -f "$SRC/config.py" ]; then
    SOURCE_DIR="$SRC"
else
    FOUND="$(find "$SRC" -maxdepth 4 -type f -name "config.py" -print -quit 2>/dev/null || true)"
    [ -n "$FOUND" ] && SOURCE_DIR="$(dirname "$FOUND")"
fi

[ -z "$SOURCE_DIR" ] && err "Could not find a directory containing config.py"
info "Config source: $SOURCE_DIR"

cp -a "$SOURCE_DIR"/. "$CONFIG_DIR"/
[ -d "$CONFIG_DIR/scripts" ] && chmod +x "$CONFIG_DIR/scripts"/*.py 2>/dev/null || true

[ -n "$TMP" ] && rm -rf "$TMP"
info "Config installed to $CONFIG_DIR"

# Python dependencies from the config
if [ -f "$CONFIG_DIR/requirements.txt" ]; then
    if [ "$DRY_RUN" = "1" ]; then
        info "[dry-run] would install Python dependencies from $CONFIG_DIR/requirements.txt"
    else
        info "Installing Python dependencies from $CONFIG_DIR/requirements.txt"
        python3 -m pip install --user -r "$CONFIG_DIR/requirements.txt"
    fi
fi

# ──[ Autostart setup ]──────────────────────────────────────────────────────
info "Configuring autostart..."

QTILE_BIN="qtile"
if cmd "$HOME/.local/bin/qtile"; then
    QTILE_BIN="$HOME/.local/bin/qtile"
elif cmd qtile; then
    QTILE_BIN="qtile"
else
    warn "Qtile is not yet available in PATH"
fi

mkdir -p "$(dirname "$XSESSION")"
mkdir -p "$(dirname "$WAYLAND_SESSION")"

if [ "$SESSION_TYPE" = "wayland" ]; then
    cat > "$WAYLAND_SESSION" <<EOF
[Desktop Entry]
Name=Qtile
Comment=Qtile Window Manager
Exec=$QTILE_BIN start --wayland
Type=Application
DesktopNames=qtile
EOF
else
    cat > "$XSESSION" <<EOF
[Desktop Entry]
Name=Qtile
Comment=Qtile Window Manager
Exec=$QTILE_BIN start
Type=Application
DesktopNames=qtile
EOF
fi

# ~/.xinitrc
if [ "$SESSION_TYPE" != "wayland" ] && { [ ! -f "$HOME/.xinitrc" ] || ! grep -q "$CONFIG_NAME" "$HOME/.xinitrc" 2>/dev/null; }; then
    echo "exec ${CONFIG_NAME} start" >> "$HOME/.xinitrc"
    info "Added to ~/.xinitrc"
fi

# ──[ Verification ]────────────────────────────────────────────────────────
info "Verifying installation..."
if cmd qtile || cmd "$HOME/.local/bin/qtile"; then
    info "Qtile: OK"
else
    warn "${CONFIG_NAME} was not found in PATH"
fi
python3 - <<'PY' >/dev/null 2>&1 || true
import qtile
PY

# ──[ Final ]────────────────────────────────────────────────────────────────
echo ""
echo -e "${G}═══════════════════════════════════════${N}"
echo -e "${G}  Qtile installed!${N}"
echo -e "${G}  Session: $SESSION_TYPE${N}"
echo -e "${G}  Config: $CONFIG_DIR${N}"
[ -n "${BACKUP:-}" ] && echo -e "${G}  Backup:  $BACKUP${N}"
echo -e "${G}  Log:    $LOG${N}"
echo -e "${G}  Run: startx for X11 or select Qtile in your display manager for Wayland${N}"
echo -e "${G}═══════════════════════════════════════${N}"
