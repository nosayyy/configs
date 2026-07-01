import os

# Клавиша-модификатор
mod = "mod4"

# Приложения по умолчанию
terminal     = "foot"
browser      = "firefox"
file_manager = "thunar"

# Пути
BASE_DIR       = os.path.expanduser("~/.config/qtile")
WALLPAPER_PATH = os.path.expanduser("~/Pictures/wallpaper.jpg")
launcher_cmd   = f"python3 {BASE_DIR}/apps/launcher.py"
notifier_cmd   = f"python3 {BASE_DIR}/apps/notifier.py"

# Внешний вид панели
BAR_SIZE      = 22
FONT_SIZE     = 12
FONT_FAMILY   = "JetBrains Mono Nerd Font"
FG            = "#ffffff"       # цвет текста
BG            = "#000000"       # фон панели (чисто чёрный)
SEP_COLOR     = "#333333"       # цвет разделителя
INACTIVE_WS   = "#555555"       # неактивный рабочий стол
URGENT_BORDER = "#ff0000"
LOW_BATTERY   = "#ff5555"       # цвет при низком заряде

# ------------------------------------------------------------
# Сетевой интерфейс
# ------------------------------------------------------------
def get_wireless_interface():
    try:
        for line in os.popen("ip -o link show").readlines():
            if "wlan" in line or "wlp" in line:
                return line.split(": ")[1]
    except:
        pass
    return "wlan0"

wlan_interface = get_wireless_interface()