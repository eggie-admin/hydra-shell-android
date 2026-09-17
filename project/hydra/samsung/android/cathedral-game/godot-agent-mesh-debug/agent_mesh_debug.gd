extends Control

# LuHm Agent Mesh v1 offline proof harness.
# No shell, no network, no privilege bridge, no background update.

const SAVE_PATH := "user://luhm_agent_mesh_debug.cfg"
const SEAL := "LUHM_AGENT_MESH_V1_20260917"

@onready var output: Label = $Safe/VBox/Output
@onready var session_label: Label = $Safe/VBox/Session

var session_id := ""
var savepoint_counter := 0
var restored := false

func _ready() -> void:
    _load_state()
    if session_id.is_empty():
        session_id = "%s-%s" % [Time.get_unix_time_from_system(), randi_range(1000, 9999)]
    _sync_session()
    _show_route("DIRECT", [], false, false, "CONTINUE", "Direct questions bypass the mesh.")

func _sync_session() -> void:
    session_label.text = "SESSION %s  |  SAVEPOINT %d  |  RESTORED %s" % [session_id, savepoint_counter, str(restored).to_upper()]

func _show_route(route: String, helpers: Array[String], critic: bool, tool_edge: bool, terminal: String, reason: String) -> void:
    var helper_text := "NONE" if helpers.is_empty() else ", ".join(helpers)
    output.text = "BOSS: LUM\nROUTE: %s\nHELPERS: %s\nCRITIC: %s\nTOOL EDGE: %s\nTERMINAL: %s\n\n%s" % [
        route,
        helper_text,
        str(critic).to_upper(),
        str(tool_edge).to_upper(),
        terminal,
        reason,
    ]

func _on_direct_pressed() -> void:
    _show_route("DIRECT", [], false, false, "CONTINUE", "Zero-helper fastpath. Lum answers Professor directly.")

func _on_context_pressed() -> void:
    _show_route("CONTEXT", ["CONTEXT"], false, false, "CONTINUE", "Minimum source-of-truth references only. Helper history = NONE.")

func _on_build_pressed() -> void:
    _show_route("BUILD", ["BUILD"], false, false, "CONTINUE", "Build blade inspects code/test receipts and returns compact evidence.")

func _on_research_pressed() -> void:
    _show_route("RESEARCH", ["RESEARCH"], false, false, "CONTINUE", "Research blade handles freshness-sensitive evidence only.")

func _on_multi_pressed() -> void:
    _show_route("CONTEXT", ["CONTEXT", "BUILD", "RESEARCH"], true, false, "CONTINUE", "Three-helper hard cap reached. Critic is required for multi-source synthesis.")

func _on_crown_required_pressed() -> void:
    _show_route("CRITIC", [], true, false, "CROWN_REQUIRED", "RECKONING request has no exact Professor authorization. Fail closed.")

func _on_authorized_edge_pressed() -> void:
    _show_route("TOOL_EXECUTOR", [], true, true, "CONTINUE", "Debug simulation only: typed edge may open after exact Professor authorization. This APK executes nothing.")

func _on_savepoint_pressed() -> void:
    savepoint_counter += 1
    var cfg := ConfigFile.new()
    cfg.set_value("mesh", "session_id", session_id)
    cfg.set_value("mesh", "savepoint_counter", savepoint_counter)
    cfg.save(SAVE_PATH)
    restored = false
    _sync_session()
    _show_route("DIRECT", [], false, false, "PROVEN", "Local debug savepoint written. Close/reopen to test restore receipt.")

func _load_state() -> void:
    var cfg := ConfigFile.new()
    if cfg.load(SAVE_PATH) == OK:
        session_id = str(cfg.get_value("mesh", "session_id", ""))
        savepoint_counter = int(cfg.get_value("mesh", "savepoint_counter", 0))
        restored = not session_id.is_empty()
