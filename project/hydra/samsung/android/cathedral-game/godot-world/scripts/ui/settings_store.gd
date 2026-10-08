extends Node
class_name LuHmSettingsStore

const SETTINGS_PATH := "user://luhm_ui_settings.json"

const DEFAULTS := {
    "display": {
        "ui_scale": 1.0,
        "window_opacity": 0.88,
        "world_dim_when_window_open": 0.08,
        "safe_area": true
    },
    "hud": {
        "minimal": true,
        "show_quest": true,
        "show_map_ping": true,
        "show_context_action": true,
        "show_lum": true,
        "show_backend_status": false
    },
    "dialogue": {
        "visual_novel_mode": true,
        "dock": "bottom",
        "height_ratio": 0.24,
        "history_button": true,
        "auto_button": true,
        "skip_button": false
    },
    "controls": {
        "tap_icon_opens_window": true,
        "tap_lum_opens_micro_menu": true,
        "long_press_lum_opens_quick_settings": true,
        "drag_windows": true,
        "snap_windows": true
    },
    "accessibility": {
        "reduced_motion": false,
        "large_text": false,
        "high_contrast": false
    },
    "backend": {
        "enabled": true,
        "mode": "local_bridge",
        "offline_fallback": true,
        "show_technical_status_in_game": false
    },
    "admin": {
        "visible_by_default": false,
        "explicit_crown_required": true,
        "game_may_grant_admin": false
    }
}

var data: Dictionary = {}

func _ready() -> void:
    load_data()

func load_data() -> Dictionary:
    data = DEFAULTS.duplicate(true)
    if FileAccess.file_exists(SETTINGS_PATH):
        var file := FileAccess.open(SETTINGS_PATH, FileAccess.READ)
        if file:
            var parsed = JSON.parse_string(file.get_as_text())
            if parsed is Dictionary:
                _deep_merge(data, parsed)
    return data

func save() -> bool:
    var file := FileAccess.open(SETTINGS_PATH, FileAccess.WRITE)
    if not file:
        return false
    file.store_string(JSON.stringify(data, "\t"))
    return true

func get_value(section: String, key: String, fallback = null):
    if data.has(section) and data[section] is Dictionary:
        return data[section].get(key, fallback)
    return fallback

func set_value(section: String, key: String, value) -> void:
    if not data.has(section) or not (data[section] is Dictionary):
        data[section] = {}
    data[section][key] = value
    save()

func reset_defaults() -> void:
    data = DEFAULTS.duplicate(true)
    save()

func _deep_merge(base: Dictionary, incoming: Dictionary) -> void:
    for key in incoming.keys():
        if base.has(key) and base[key] is Dictionary and incoming[key] is Dictionary:
            _deep_merge(base[key], incoming[key])
        else:
            base[key] = incoming[key]
