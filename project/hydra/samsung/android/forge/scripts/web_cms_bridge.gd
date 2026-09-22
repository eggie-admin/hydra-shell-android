extends Node

# LUHM_MULTI_TIER_BRIDGE_V1
# Web Cathedral is a presentation tier. Native Godot remains the runtime host.

signal cms_ready
signal cms_message(message: String)

const PLUGIN_NAME := "CathedralAndroid"
var _plugin = null

func _ready() -> void:
    if OS.get_name() != "Android":
        return
    if not Engine.has_singleton(PLUGIN_NAME):
        push_error("CathedralAndroid plugin is missing")
        return
    _plugin = Engine.get_singleton(PLUGIN_NAME)
    if _plugin.has_signal("cms_message"):
        _plugin.connect("cms_message", _on_cms_message)
    await get_tree().create_timer(0.35).timeout
    _plugin.openCms()

func open_cms() -> void:
    if _plugin:
        _plugin.openCms()

func close_cms() -> void:
    if _plugin:
        _plugin.closeCms()

func send_to_cms(message: Dictionary) -> void:
    if _plugin:
        _plugin.postToCms(JSON.stringify(message))

func _on_cms_message(raw: String) -> void:
    if raw.length() > 32768:
        push_warning("Rejected oversized CMS bridge message")
        return
    cms_message.emit(raw)
    var parsed = JSON.parse_string(raw)
    if not parsed is Dictionary:
        return
    var message: Dictionary = parsed
    var kind := String(message.get("type", ""))
    var payload = message.get("payload", {})
    if not payload is Dictionary:
        payload = {}
    var host := get_parent()
    match kind:
        "cms.ready":
            cms_ready.emit()
        "ui.world.enter":
            if host and host.has_method("enter_world_mode"):
                host.enter_world_mode()
        "ui.cathedral.enter":
            if host and host.has_method("exit_world_mode"):
                host.exit_world_mode()
        "app.window.immersive":
            if _plugin and _plugin.has_method("setImmersiveKiosk"):
                _plugin.setImmersiveKiosk(true)
        "app.window.system_bars":
            if _plugin and _plugin.has_method("setImmersiveKiosk"):
                _plugin.setImmersiveKiosk(false)
        "app.device.snapshot":
            if _plugin and _plugin.has_method("deviceSnapshot"):
                var snapshot = JSON.parse_string(_plugin.deviceSnapshot())
                if not snapshot is Dictionary:
                    snapshot = {}
                send_to_cms({"type": "app.device.snapshot.result", "payload": snapshot})
        "app.quit":
            get_tree().quit()
        "godot.window.open":
            var allowed_panels := ["renderQueue", "lumAgent", "cutsceneDirector", "cms"]
            var panel := String(payload.get("panel", ""))
            if panel in allowed_panels and host and host.has_method("open_tool_window"):
                host.open_tool_window(panel)
        "godot.avatar.state":
            var allowed_states := ["idle", "thinking", "speaking", "rendering", "error"]
            var state := String(payload.get("state", "idle"))
            if state in allowed_states and host and host.has_method("set_avatar_state"):
                host.set_avatar_state(StringName(state))
        _:
            pass
