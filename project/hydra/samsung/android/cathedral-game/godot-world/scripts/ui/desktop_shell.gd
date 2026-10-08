extends CanvasLayer
class_name LuHmDesktopShell

signal typed_intent(intent_id: String, payload: Dictionary)
signal dialogue_visibility_changed(visible: bool)

const WindowManagerScript = preload("res://scripts/ui/window_manager.gd")
const SettingsStoreScript = preload("res://scripts/ui/settings_store.gd")
const PROOF_SAVE_PATH := "user://luhmos_physical_proof.cfg"

var manager: LuHmWindowManager
var settings_store: LuHmSettingsStore
var _root: Control
var _launcher_panel: PanelContainer
var _dialogue_dock: PanelContainer
var _dialogue_speaker: Label
var _dialogue_line: Label
var _settings_window: PanelContainer
var _codex_window: PanelContainer
var _backend_window: PanelContainer
var _quest_window: PanelContainer
var _proof_window: PanelContainer
var _proof_label: Label

var proof_ui_mode := "SPRITE_BUBBLE"
var proof_realm := "GAME"
var proof_session_id := ""
var proof_counter := 0
var proof_last_saved_session := "NONE"

func _ready() -> void:
    layer = 20
    proof_session_id = "%s-%s" % [Time.get_unix_time_from_system(), randi_range(1000, 9999)]
    settings_store = SettingsStoreScript.new()
    add_child(settings_store)

    _root = Control.new()
    _root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _root.mouse_filter = Control.MOUSE_FILTER_PASS
    add_child(_root)

    manager = WindowManagerScript.new()
    manager.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    manager.mouse_filter = Control.MOUSE_FILTER_PASS
    _root.add_child(manager)

    _build_launcher()
    _build_dialogue_dock()
    _build_windows()
    _load_proof_state()
    _apply_saved_settings()
    _sync_proof()

func _build_launcher() -> void:
    var launcher := Button.new()
    launcher.text = "▦"
    launcher.tooltip_text = "LuHm windows"
    launcher.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
    launcher.position = Vector2(-86, 84)
    launcher.size = Vector2(58, 58)
    launcher.add_theme_font_size_override("font_size", 26)
    launcher.add_theme_color_override("font_color", Color("f6c9ff"))
    launcher.add_theme_stylebox_override("normal", _panel_style(Color(0.03, 0.02, 0.05, 0.42), Color(0.9, 0.45, 1.0, 0.35), 16))
    launcher.add_theme_stylebox_override("pressed", _panel_style(Color(0.17, 0.06, 0.20, 0.92), Color("ff66b7"), 16))
    launcher.pressed.connect(_toggle_launcher)
    _root.add_child(launcher)

    _launcher_panel = PanelContainer.new()
    _launcher_panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
    _launcher_panel.position = Vector2(-260, 150)
    _launcher_panel.size = Vector2(230, 310)
    _launcher_panel.visible = false
    _launcher_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.025, 0.018, 0.04, 0.95), Color("7d5b87"), 18))
    _root.add_child(_launcher_panel)

    var list := VBoxContainer.new()
    list.add_theme_constant_override("separation", 8)
    _launcher_panel.add_child(list)
    list.add_child(_launcher_item("QUEST", "quest"))
    list.add_child(_launcher_item("CODEX", "codex"))
    list.add_child(_launcher_item("SETTINGS", "settings"))
    list.add_child(_launcher_item("BACKEND", "backend"))
    list.add_child(_launcher_item("PROOF", "proof"))

func _launcher_item(label_text: String, window_id: String) -> Button:
    var button := Button.new()
    button.text = label_text
    button.custom_minimum_size = Vector2(190, 48)
    button.alignment = HORIZONTAL_ALIGNMENT_LEFT
    button.add_theme_font_size_override("font_size", 16)
    button.pressed.connect(func():
        manager.toggle_window(window_id)
        _launcher_panel.visible = false
        emit_signal("typed_intent", "ui.window.toggle", {"window_id": window_id})
    )
    return button

func _build_dialogue_dock() -> void:
    _dialogue_dock = PanelContainer.new()
    _dialogue_dock.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
    _dialogue_dock.offset_left = 18
    _dialogue_dock.offset_right = -18
    _dialogue_dock.offset_top = -276
    _dialogue_dock.offset_bottom = -18
    _dialogue_dock.visible = false
    _dialogue_dock.add_theme_stylebox_override("panel", _panel_style(Color(0.025, 0.018, 0.04, 0.94), Color(1.0, 0.35, 0.70, 0.52), 22))
    _root.add_child(_dialogue_dock)

    var column := VBoxContainer.new()
    column.add_theme_constant_override("separation", 8)
    _dialogue_dock.add_child(column)

    var bar := HBoxContainer.new()
    column.add_child(bar)
    _dialogue_speaker = Label.new()
    _dialogue_speaker.text = "LUM"
    _dialogue_speaker.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _dialogue_speaker.add_theme_font_size_override("font_size", 19)
    _dialogue_speaker.add_theme_color_override("font_color", Color("ff78bd"))
    bar.add_child(_dialogue_speaker)
    var close := Button.new()
    close.text = "×"
    close.tooltip_text = "Hide dialogue"
    close.pressed.connect(hide_dialogue)
    bar.add_child(close)

    _dialogue_line = Label.new()
    _dialogue_line.text = "The world stays visible. Dialogue floats over the stage."
    _dialogue_line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _dialogue_line.size_flags_vertical = Control.SIZE_EXPAND_FILL
    _dialogue_line.add_theme_font_size_override("font_size", 22)
    _dialogue_line.add_theme_color_override("font_color", Color("f8edf9"))
    column.add_child(_dialogue_line)

    var controls := HBoxContainer.new()
    controls.add_theme_constant_override("separation", 8)
    column.add_child(controls)
    var log_button := _small_button("LOG")
    log_button.pressed.connect(func(): manager.toggle_window("codex"))
    controls.add_child(log_button)
    var auto_button := _small_button("AUTO")
    auto_button.toggle_mode = true
    auto_button.toggled.connect(func(enabled: bool):
        emit_signal("typed_intent", "game.dialogue.auto", {"enabled": enabled})
    )
    controls.add_child(auto_button)
    var settings_button := _small_button("SETTINGS")
    settings_button.pressed.connect(func(): manager.toggle_window("settings"))
    controls.add_child(settings_button)

func _build_windows() -> void:
    var quest_parts := _make_window("QUEST", Vector2(46, 150), Vector2(560, 350))
    _quest_window = quest_parts.panel
    quest_parts.body.text = "CORKTOWN SWITCHYARD\n\nFind the contact signal beyond the rails.\nIndustry · ruin · spirits · opportunity."
    manager.register_window("quest", _quest_window, quest_parts.header)

    var codex_parts := _make_window("CODEX", Vector2(72, 196), Vector2(610, 520))
    _codex_window = codex_parts.panel
    codex_parts.body.text = "LUHM FIELD CODEX\n\nCONTACT  Talk / recruit\nBOND     Character interaction\nDESCEND  Advance the dungeon\nCROWN    Explicit admin cockpit summon\n\nGAME state never grants ADMIN authority."
    manager.register_window("codex", _codex_window, codex_parts.header)

    var backend_parts := _make_window("FRONT / BACK", Vector2(106, 242), Vector2(650, 440))
    _backend_window = backend_parts.panel
    backend_parts.body.text = "FRONT END\nGodot 4 world + CanvasLayer windows + VN dialogue\n\nBACK END\nTyped local bridge to the existing control plane\nFastAPI / SQLite where already configured\n\nMODE\nOffline-safe. No direct shell. No hidden network fetch."
    manager.register_window("backend", _backend_window, backend_parts.header)

    var proof_parts := _make_window("PHYSICAL PROOF", Vector2(56, 132), Vector2(720, 720))
    _proof_window = proof_parts.panel
    proof_parts.body.queue_free()
    _populate_proof(proof_parts.content)
    manager.register_window("proof", _proof_window, proof_parts.header)

    var settings_parts := _make_window("SETTINGS", Vector2(84, 178), Vector2(680, 670))
    _settings_window = settings_parts.panel
    settings_parts.body.queue_free()
    _populate_settings(settings_parts.content)
    manager.register_window("settings", _settings_window, settings_parts.header)

func _make_window(title_text: String, pos: Vector2, window_size: Vector2) -> Dictionary:
    var panel := PanelContainer.new()
    panel.position = pos
    panel.size = window_size
    panel.add_theme_stylebox_override("panel", _panel_style(Color(0.025, 0.018, 0.04, 0.96), Color("75537f"), 18))
    manager.add_child(panel)

    var column := VBoxContainer.new()
    column.add_theme_constant_override("separation", 10)
    panel.add_child(column)

    var header := HBoxContainer.new()
    header.mouse_filter = Control.MOUSE_FILTER_STOP
    header.custom_minimum_size = Vector2(0, 48)
    column.add_child(header)

    var title := Label.new()
    title.text = title_text
    title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    title.add_theme_font_size_override("font_size", 18)
    title.add_theme_color_override("font_color", Color("f6c9ff"))
    header.add_child(title)

    var close := Button.new()
    close.text = "×"
    close.custom_minimum_size = Vector2(48, 42)
    header.add_child(close)

    var content := MarginContainer.new()
    content.size_flags_vertical = Control.SIZE_EXPAND_FILL
    column.add_child(content)

    var body := Label.new()
    body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    body.size_flags_vertical = Control.SIZE_EXPAND_FILL
    body.add_theme_font_size_override("font_size", 18)
    body.add_theme_color_override("font_color", Color("eee5f0"))
    content.add_child(body)

    close.pressed.connect(func(): panel.visible = false)
    return {"panel": panel, "header": header, "content": content, "body": body}

func _populate_proof(content: MarginContainer) -> void:
    var column := VBoxContainer.new()
    column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    column.size_flags_vertical = Control.SIZE_EXPAND_FILL
    column.add_theme_constant_override("separation", 12)
    content.add_child(column)

    _proof_label = Label.new()
    _proof_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _proof_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _proof_label.add_theme_font_size_override("font_size", 17)
    _proof_label.add_theme_color_override("font_color", Color("a5f4d5"))
    column.add_child(_proof_label)

    var mode_title := Label.new()
    mode_title.text = "PRESENTATION MODE"
    column.add_child(mode_title)
    var mode_row := HBoxContainer.new()
    mode_row.add_theme_constant_override("separation", 8)
    column.add_child(mode_row)
    var bubble := _small_button("BUBBLE")
    bubble.pressed.connect(func(): _set_proof_mode("SPRITE_BUBBLE"))
    mode_row.add_child(bubble)
    var deck := _small_button("DECK")
    deck.pressed.connect(func(): _set_proof_mode("WIDGET_DECK"))
    mode_row.add_child(deck)
    var full := _small_button("FULL")
    full.pressed.connect(func(): _set_proof_mode("FULL_COCKPIT"))
    mode_row.add_child(full)

    var realm_title := Label.new()
    realm_title.text = "PRESENTATION REALM"
    column.add_child(realm_title)
    var realm_row := HBoxContainer.new()
    realm_row.add_theme_constant_override("separation", 8)
    column.add_child(realm_row)
    var game := _small_button("GAME")
    game.pressed.connect(func(): _set_proof_realm("GAME"))
    realm_row.add_child(game)
    var admin := _small_button("ADMIN")
    admin.pressed.connect(func(): _set_proof_realm("ADMIN"))
    realm_row.add_child(admin)
    var system := _small_button("SYSTEM")
    system.pressed.connect(func(): _set_proof_realm("SYSTEM"))
    realm_row.add_child(system)

    var save := Button.new()
    save.text = "SAVEPOINT // LOCAL PROOF RECEIPT"
    save.custom_minimum_size = Vector2(0, 52)
    save.pressed.connect(_save_proof_state)
    column.add_child(save)

    var boundary := Label.new()
    boundary.text = "GAME cannot grant ADMIN authority. Realm/mode controls are presentation only.\nActual ADMIN cockpit still requires explicit Lum → CROWN.\nNo shell, no network, no privilege bridge, no silent install."
    boundary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    boundary.add_theme_color_override("font_color", Color("c7b8cc"))
    column.add_child(boundary)

func _populate_settings(content: MarginContainer) -> void:
    var scroll := ScrollContainer.new()
    scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
    content.add_child(scroll)

    var list := VBoxContainer.new()
    list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    list.add_theme_constant_override("separation", 14)
    scroll.add_child(list)

    var heading := Label.new()
    heading.text = "DISPLAY / HUD / DIALOGUE / ACCESSIBILITY"
    heading.add_theme_font_size_override("font_size", 16)
    list.add_child(heading)

    var scale_label := Label.new()
    scale_label.text = "UI scale"
    list.add_child(scale_label)
    var scale_slider := HSlider.new()
    scale_slider.min_value = 0.85
    scale_slider.max_value = 1.25
    scale_slider.step = 0.05
    scale_slider.value = float(settings_store.get_value("display", "ui_scale", 1.0))
    scale_slider.value_changed.connect(_on_ui_scale_changed)
    list.add_child(scale_slider)

    var vn := CheckButton.new()
    vn.text = "Visual novel dialogue dock"
    vn.button_pressed = bool(settings_store.get_value("dialogue", "visual_novel_mode", true))
    vn.toggled.connect(_on_vn_toggled)
    list.add_child(vn)

    var backend_status := CheckButton.new()
    backend_status.text = "Show backend status in game"
    backend_status.button_pressed = bool(settings_store.get_value("backend", "show_technical_status_in_game", false))
    backend_status.toggled.connect(_on_backend_status_toggled)
    list.add_child(backend_status)

    var reduced_motion := CheckButton.new()
    reduced_motion.text = "Reduced motion"
    reduced_motion.button_pressed = bool(settings_store.get_value("accessibility", "reduced_motion", false))
    reduced_motion.toggled.connect(_on_reduced_motion_toggled)
    list.add_child(reduced_motion)

    var policy := Label.new()
    policy.text = "ADMIN stays hidden behind explicit Lum → CROWN.\nGAME cannot grant ADMIN authority."
    policy.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    policy.add_theme_color_override("font_color", Color("c7b8cc"))
    list.add_child(policy)

    var reset := Button.new()
    reset.text = "RESET UI DEFAULTS"
    reset.pressed.connect(_reset_defaults)
    list.add_child(reset)

func _load_proof_state() -> void:
    var cfg := ConfigFile.new()
    var err := cfg.load(PROOF_SAVE_PATH)
    if err == OK:
        proof_counter = int(cfg.get_value("proof", "counter", 0))
        proof_last_saved_session = str(cfg.get_value("proof", "session_id", "NONE"))
    proof_ui_mode = "SPRITE_BUBBLE"
    proof_realm = "GAME"

func _save_proof_state() -> void:
    proof_counter += 1
    var cfg := ConfigFile.new()
    cfg.set_value("proof", "counter", proof_counter)
    cfg.set_value("proof", "session_id", proof_session_id)
    cfg.set_value("proof", "mode", proof_ui_mode)
    cfg.set_value("proof", "realm", proof_realm)
    var err := cfg.save(PROOF_SAVE_PATH)
    if err == OK:
        proof_last_saved_session = proof_session_id
        emit_signal("typed_intent", "proof.savepoint.sealed", {"counter": proof_counter})
    else:
        emit_signal("typed_intent", "proof.savepoint.error", {"error": err})
    _sync_proof()

func _set_proof_mode(next_mode: String) -> void:
    proof_ui_mode = next_mode
    emit_signal("typed_intent", "proof.ui.mode", {"mode": next_mode})
    _sync_proof()

func _set_proof_realm(next_realm: String) -> void:
    proof_realm = next_realm
    emit_signal("typed_intent", "proof.ui.realm", {"realm": next_realm, "authority_changed": false})
    _sync_proof()

func _sync_proof() -> void:
    if _proof_label:
        _proof_label.text = "PHYSICAL PROOF HARNESS\nMODE: %s\nREALM: %s\nSESSION: %s\nSAVEPOINT: %d\nRESTORED SESSION: %s" % [proof_ui_mode, proof_realm, proof_session_id, proof_counter, proof_last_saved_session]

func show_dialogue(speaker: String, line: String) -> void:
    if not bool(settings_store.get_value("dialogue", "visual_novel_mode", true)):
        return
    _dialogue_speaker.text = speaker
    _dialogue_line.text = line
    _dialogue_dock.visible = true
    emit_signal("dialogue_visibility_changed", true)

func hide_dialogue() -> void:
    _dialogue_dock.visible = false
    emit_signal("dialogue_visibility_changed", false)

func toggle_window(window_id: String) -> void:
    manager.toggle_window(window_id)

func toggle_launcher() -> void:
    _toggle_launcher()

func _toggle_launcher() -> void:
    _launcher_panel.visible = not _launcher_panel.visible

func _on_ui_scale_changed(value: float) -> void:
    settings_store.set_value("display", "ui_scale", value)
    manager.scale = Vector2(value, value)
    emit_signal("typed_intent", "ui.settings.changed", {"display.ui_scale": value})

func _on_vn_toggled(enabled: bool) -> void:
    settings_store.set_value("dialogue", "visual_novel_mode", enabled)
    if not enabled:
        hide_dialogue()
    emit_signal("typed_intent", "ui.settings.changed", {"dialogue.visual_novel_mode": enabled})

func _on_backend_status_toggled(enabled: bool) -> void:
    settings_store.set_value("backend", "show_technical_status_in_game", enabled)
    emit_signal("typed_intent", "ui.settings.changed", {"backend.show_technical_status_in_game": enabled})

func _on_reduced_motion_toggled(enabled: bool) -> void:
    settings_store.set_value("accessibility", "reduced_motion", enabled)
    emit_signal("typed_intent", "ui.settings.changed", {"accessibility.reduced_motion": enabled})

func _reset_defaults() -> void:
    settings_store.reset_defaults()
    manager.scale = Vector2.ONE
    hide_dialogue()
    emit_signal("typed_intent", "ui.settings.reset", {})

func _apply_saved_settings() -> void:
    var scale_value := float(settings_store.get_value("display", "ui_scale", 1.0))
    manager.scale = Vector2(scale_value, scale_value)

func _small_button(label_text: String) -> Button:
    var button := Button.new()
    button.text = label_text
    button.custom_minimum_size = Vector2(110, 42)
    return button

func _panel_style(bg: Color, border: Color, radius: int) -> StyleBoxFlat:
    var style := StyleBoxFlat.new()
    style.bg_color = bg
    style.border_color = border
    style.set_border_width_all(2)
    style.corner_radius_top_left = radius
    style.corner_radius_top_right = radius
    style.corner_radius_bottom_left = radius
    style.corner_radius_bottom_right = radius
    style.content_margin_left = 14
    style.content_margin_right = 14
    style.content_margin_top = 10
    style.content_margin_bottom = 10
    return style
