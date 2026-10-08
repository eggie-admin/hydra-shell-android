extends Node

# KAI9000_GODOT_WORLD_FIRST_HUD_V2
# LUHM_OS_WINDOWS_VN_CATHEDRAL_1_0_8
# Native Godot 4 world owns the screen. HUD stays minimal. Lightweight windows
# and visual-novel dialogue float over the stage. The WebView cockpit is opened
# only by an explicit CROWN gesture from the Lum micro menu.

const PLUGIN_NAME := "CathedralAndroid"
const WORLD_TITLE := "CORKTOWN SWITCHYARD"
const WORLD_SUBTITLE := "INDUSTRY · RUIN · SPIRITS · OPPORTUNITY"
const DesktopShellScript = preload("res://scripts/ui/desktop_shell.gd")

var _plugin = null
var _camera: Camera3D
var _lum_sprite: Sprite3D
var _contact_marker: Label3D
var _hud_root: Control
var _micro_menu: PanelContainer
var _quest_panel: PanelContainer
var _status_label: Label
var _desktop_shell = null
var _world_time := 0.0
var _interaction_step := 0

func _ready() -> void:
    _build_world()
    _build_hud()
    _build_desktop_shell()
    if OS.get_name() == "Android" and Engine.has_singleton(PLUGIN_NAME):
        _plugin = Engine.get_singleton(PLUGIN_NAME)
    _set_status("WORLD FIRST · VN DESKTOP · WHISPER · READY")

func _process(delta: float) -> void:
    _world_time += delta
    if _camera:
        var drift := sin(_world_time * 0.18) * 0.42
        _camera.position.x = drift
        _camera.look_at(Vector3(0.0, 1.9, -5.0), Vector3.UP)
    if _lum_sprite:
        _lum_sprite.position.y = 1.55 + sin(_world_time * 1.7) * 0.08
    if _contact_marker:
        var pulse := 0.82 + sin(_world_time * 2.4) * 0.18
        _contact_marker.modulate = Color(0.45, 0.95, 1.0, pulse)

func _build_world() -> void:
    var environment := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color("05030a")
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color("4d235d")
    env.ambient_light_energy = 0.62
    env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    env.glow_enabled = true
    environment.environment = env
    add_child(environment)

    var key := DirectionalLight3D.new()
    key.rotation_degrees = Vector3(-52.0, -24.0, 0.0)
    key.light_color = Color("ffd8ec")
    key.light_energy = 1.25
    key.shadow_enabled = true
    add_child(key)

    var rim := OmniLight3D.new()
    rim.position = Vector3(0.0, 4.2, -8.0)
    rim.light_color = Color("ff2e9b")
    rim.light_energy = 9.0
    rim.omni_range = 18.0
    add_child(rim)

    _camera = Camera3D.new()
    _camera.position = Vector3(0.0, 6.4, 12.8)
    _camera.fov = 58.0
    _camera.current = true
    add_child(_camera)
    _camera.look_at(Vector3(0.0, 1.9, -5.0), Vector3.UP)

    _add_box("Ground", Vector3(0.0, -0.22, -5.0), Vector3(24.0, 0.35, 34.0), Color("09070e"), 0.15)
    _add_box("RailL", Vector3(-1.15, 0.03, -5.0), Vector3(0.10, 0.08, 30.0), Color("d7c7e7"), 0.25)
    _add_box("RailR", Vector3(1.15, 0.03, -5.0), Vector3(0.10, 0.08, 30.0), Color("d7c7e7"), 0.25)

    for z in range(-18, 8, 2):
        _add_box("Tie_%s" % z, Vector3(0.0, -0.02, float(z)), Vector3(3.1, 0.10, 0.18), Color("231423"), 0.0)

    var building_specs := [
        [Vector3(-6.6, 2.0, -6.0), Vector3(3.1, 4.0, 4.8), Color("17101d")],
        [Vector3(6.0, 2.8, -7.0), Vector3(3.0, 5.6, 4.0), Color("15101c")],
        [Vector3(-7.8, 3.3, -13.0), Vector3(4.0, 6.6, 4.5), Color("110e18")],
        [Vector3(7.4, 4.1, -14.5), Vector3(4.2, 8.2, 4.8), Color("120d18")],
        [Vector3(-5.4, 2.5, -18.5), Vector3(2.7, 5.0, 3.0), Color("160f1e")],
        [Vector3(5.0, 3.2, -19.0), Vector3(2.8, 6.4, 3.1), Color("160f1e")]
    ]
    for spec in building_specs:
        _add_box("Block", spec[0], spec[1], spec[2], 0.0)

    _add_cathedral(Vector3(0.0, 0.0, -18.0))
    _add_neon_sign(Vector3(-4.8, 2.8, -4.3), "CORKTOWN")

    var lum_texture := load("res://assets/lum_world_sprite.svg") as Texture2D
    if lum_texture:
        _lum_sprite = Sprite3D.new()
        _lum_sprite.texture = lum_texture
        _lum_sprite.pixel_size = 0.0092
        _lum_sprite.position = Vector3(2.25, 1.55, -3.3)
        _lum_sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
        _lum_sprite.no_depth_test = true
        add_child(_lum_sprite)

    _contact_marker = Label3D.new()
    _contact_marker.text = "◇ CONTACT"
    _contact_marker.font_size = 42
    _contact_marker.position = Vector3(-2.35, 1.45, -5.2)
    _contact_marker.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    _contact_marker.outline_size = 10
    _contact_marker.outline_modulate = Color(0.02, 0.01, 0.03, 0.9)
    _contact_marker.modulate = Color("78e9ff")
    add_child(_contact_marker)

    var zone := Label3D.new()
    zone.text = WORLD_TITLE
    zone.font_size = 34
    zone.position = Vector3(0.0, 0.45, -9.0)
    zone.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    zone.modulate = Color("ff66b7")
    zone.outline_size = 8
    zone.outline_modulate = Color(0.0, 0.0, 0.0, 0.8)
    add_child(zone)

func _add_cathedral(origin: Vector3) -> void:
    _add_box("CathedralBody", origin + Vector3(0.0, 3.2, 0.0), Vector3(5.0, 6.4, 4.5), Color("120c1b"), 0.0)
    _add_box("TowerL", origin + Vector3(-2.4, 5.3, 0.15), Vector3(1.3, 10.6, 1.8), Color("100b18"), 0.0)
    _add_box("TowerR", origin + Vector3(2.4, 5.3, 0.15), Vector3(1.3, 10.6, 1.8), Color("100b18"), 0.0)
    _add_spire(origin + Vector3(-2.4, 11.2, 0.15))
    _add_spire(origin + Vector3(2.4, 11.2, 0.15))

    var rose := MeshInstance3D.new()
    var rose_mesh := CylinderMesh.new()
    rose_mesh.top_radius = 0.95
    rose_mesh.bottom_radius = 0.95
    rose_mesh.height = 0.10
    rose.mesh = rose_mesh
    rose.rotation_degrees = Vector3(90.0, 0.0, 0.0)
    rose.position = origin + Vector3(0.0, 4.0, 2.30)
    rose.material_override = _material(Color("ff3fa4"), 6.0)
    add_child(rose)

func _add_spire(pos: Vector3) -> void:
    var spire := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 0.0
    mesh.bottom_radius = 0.62
    mesh.height = 3.0
    spire.mesh = mesh
    spire.position = pos
    spire.material_override = _material(Color("1b1025"), 0.0)
    add_child(spire)

func _add_neon_sign(pos: Vector3, text_value: String) -> void:
    var label := Label3D.new()
    label.text = text_value
    label.font_size = 48
    label.position = pos
    label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    label.modulate = Color("ff3fa4")
    label.outline_size = 10
    label.outline_modulate = Color("381026")
    add_child(label)

func _add_box(name_value: String, pos: Vector3, size_value: Vector3, color_value: Color, emission_energy: float) -> void:
    var mesh_instance := MeshInstance3D.new()
    mesh_instance.name = name_value
    var mesh := BoxMesh.new()
    mesh.size = size_value
    mesh_instance.mesh = mesh
    mesh_instance.position = pos
    mesh_instance.material_override = _material(color_value, emission_energy)
    add_child(mesh_instance)

func _material(color_value: Color, emission_energy: float) -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color_value
    mat.metallic = 0.18
    mat.roughness = 0.72
    if emission_energy > 0.0:
        mat.emission_enabled = true
        mat.emission = color_value
        mat.emission_energy_multiplier = emission_energy
    return mat

func _build_hud() -> void:
    var layer := CanvasLayer.new()
    layer.layer = 10
    add_child(layer)

    _hud_root = Control.new()
    _hud_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    _hud_root.mouse_filter = Control.MOUSE_FILTER_PASS
    layer.add_child(_hud_root)

    var quest := _hud_button("◇", Color("ff66b7"))
    quest.position = Vector2(22, 28)
    quest.size = Vector2(66, 66)
    quest.tooltip_text = "Quest"
    quest.pressed.connect(_toggle_quest)
    _hud_root.add_child(quest)

    var map := _hud_button("⌖", Color("78e9ff"))
    map.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
    map.position = Vector2(22, -92)
    map.size = Vector2(66, 66)
    map.tooltip_text = "Map"
    map.pressed.connect(_map_ping)
    _hud_root.add_child(map)

    var action := _hud_button("A", Color("ffffff"))
    action.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
    action.position = Vector2(-42, -98)
    action.size = Vector2(84, 72)
    action.tooltip_text = "Context action"
    action.pressed.connect(_context_action)
    _hud_root.add_child(action)

    var lum_texture := load("res://assets/lum_hud_icon.svg") as Texture2D
    var lum := Button.new()
    lum.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
    lum.position = Vector2(-116, -120)
    lum.size = Vector2(96, 96)
    lum.text = ""
    lum.icon = lum_texture
    lum.expand_icon = true
    lum.flat = true
    lum.tooltip_text = "Lum"
    lum.pressed.connect(_toggle_micro_menu)
    _hud_root.add_child(lum)

    _status_label = Label.new()
    _status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _status_label.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
    _status_label.position = Vector2(-430, 28)
    _status_label.size = Vector2(400, 44)
    _status_label.add_theme_color_override("font_color", Color("b8a9bf"))
    _status_label.add_theme_font_size_override("font_size", 18)
    _hud_root.add_child(_status_label)

    _micro_menu = PanelContainer.new()
    _micro_menu.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
    _micro_menu.position = Vector2(-470, -218)
    _micro_menu.size = Vector2(438, 78)
    _micro_menu.visible = false
    _micro_menu.add_theme_stylebox_override("panel", _panel_style(Color(0.04, 0.02, 0.06, 0.92), Color("ff66b7")))
    _hud_root.add_child(_micro_menu)

    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 8)
    _micro_menu.add_child(row)

    var pet := _mini_button("PET")
    pet.pressed.connect(_pet_lum)
    row.add_child(pet)
    var quest_micro := _mini_button("QUEST")
    quest_micro.pressed.connect(_toggle_quest)
    row.add_child(quest_micro)
    var desk := _mini_button("DESK")
    desk.pressed.connect(_toggle_desktop)
    row.add_child(desk)
    var crown := _mini_button("CROWN")
    crown.pressed.connect(_summon_cockpit)
    row.add_child(crown)

    _quest_panel = PanelContainer.new()
    _quest_panel.position = Vector2(22, 104)
    _quest_panel.size = Vector2(450, 122)
    _quest_panel.visible = false
    _quest_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.03, 0.02, 0.05, 0.90), Color("ff66b7")))
    _hud_root.add_child(_quest_panel)
    var quest_text := Label.new()
    quest_text.text = "CORKTOWN SWITCHYARD\nFind the contact signal beyond the rails.\n" + WORLD_SUBTITLE
    quest_text.add_theme_font_size_override("font_size", 18)
    quest_text.add_theme_color_override("font_color", Color("f4eafa"))
    _quest_panel.add_child(quest_text)

func _build_desktop_shell() -> void:
    _desktop_shell = DesktopShellScript.new()
    add_child(_desktop_shell)
    _desktop_shell.typed_intent.connect(_on_desktop_intent)
    _desktop_shell.dialogue_visibility_changed.connect(_on_dialogue_visibility_changed)

func _hud_button(text_value: String, accent: Color) -> Button:
    var button := Button.new()
    button.text = text_value
    button.add_theme_font_size_override("font_size", 30)
    button.add_theme_color_override("font_color", accent)
    button.add_theme_stylebox_override("normal", _panel_style(Color(0.03, 0.02, 0.05, 0.36), Color(accent, 0.35)))
    button.add_theme_stylebox_override("hover", _panel_style(Color(0.08, 0.04, 0.11, 0.72), accent))
    button.add_theme_stylebox_override("pressed", _panel_style(Color(0.15, 0.05, 0.16, 0.90), accent))
    return button

func _mini_button(text_value: String) -> Button:
    var button := Button.new()
    button.text = text_value
    button.custom_minimum_size = Vector2(94, 56)
    button.add_theme_font_size_override("font_size", 16)
    button.add_theme_color_override("font_color", Color("f8edf9"))
    button.add_theme_stylebox_override("normal", _panel_style(Color(0.06, 0.04, 0.08, 0.92), Color("5f4968")))
    button.add_theme_stylebox_override("pressed", _panel_style(Color(0.30, 0.08, 0.28, 0.95), Color("ff66b7")))
    return button

func _panel_style(bg: Color, border: Color) -> StyleBoxFlat:
    var style := StyleBoxFlat.new()
    style.bg_color = bg
    style.border_color = border
    style.set_border_width_all(2)
    style.corner_radius_top_left = 18
    style.corner_radius_top_right = 18
    style.corner_radius_bottom_left = 18
    style.corner_radius_bottom_right = 18
    style.content_margin_left = 14
    style.content_margin_right = 14
    style.content_margin_top = 10
    style.content_margin_bottom = 10
    return style

func _toggle_micro_menu() -> void:
    _micro_menu.visible = not _micro_menu.visible
    _set_status("LUM MICRO MENU · explicit summon only" if _micro_menu.visible else "WORLD FIRST · VN DESKTOP · WHISPER · READY")

func _toggle_desktop() -> void:
    _micro_menu.visible = false
    if _desktop_shell:
        _desktop_shell.toggle_launcher()
    _set_status("DESKTOP ICONS · lightweight windows over world")

func _toggle_quest() -> void:
    _quest_panel.visible = not _quest_panel.visible
    _set_status("QUEST SIGIL · CORKTOWN" if _quest_panel.visible else "WORLD FIRST · VN DESKTOP · WHISPER · READY")

func _map_ping() -> void:
    _set_status("MAP PING · CORKTOWN SWITCHYARD · DETROIT-ISH")

func _context_action() -> void:
    _interaction_step = (_interaction_step + 1) % 3
    match _interaction_step:
        0:
            _contact_marker.text = "◇ CONTACT"
            _set_status("CONTACT READY · no admin authority")
            if _desktop_shell:
                _desktop_shell.show_dialogue("LUM", "Signal's back. CONTACT is game-space only. No crown keys hiding in the dialogue box.")
        1:
            _contact_marker.text = "◇ BOND"
            _set_status("BOND · GAME ONLY")
            if _desktop_shell:
                _desktop_shell.show_dialogue("LUM", "Bond event queued. The Cathedral stays visible behind the dialogue dock.")
        2:
            _contact_marker.text = "◇ DESCEND"
            _set_status("DESCEND · next room staged")
            if _desktop_shell:
                _desktop_shell.show_dialogue("LUM", "Next room is staged. DESCEND when you're ready, Professor.")

func _pet_lum() -> void:
    _set_status("LUM · suspiciously cheerful · GAME ONLY")
    if _desktop_shell:
        _desktop_shell.show_dialogue("LUM", "Pet received. Still not sudo. Still cute.")
    if _lum_sprite:
        _lum_sprite.scale = Vector3.ONE * 1.08
        await get_tree().create_timer(0.16).timeout
        if is_instance_valid(_lum_sprite):
            _lum_sprite.scale = Vector3.ONE

func _summon_cockpit() -> void:
    _micro_menu.visible = false
    _set_status("CROWN · explicit cockpit summon")
    if _plugin:
        _plugin.openCms()
    else:
        push_warning("CathedralAndroid cockpit plugin unavailable on this runtime")
        _set_status("CROWN · cockpit plugin unavailable")

func _on_desktop_intent(intent_id: String, payload: Dictionary) -> void:
    match intent_id:
        "ui.window.toggle":
            _set_status("WINDOW · %s · PRESENTATION ONLY" % String(payload.get("window_id", "unknown")).to_upper())
        "ui.settings.changed":
            _set_status("SETTINGS SAVED · local UI only")
        "ui.settings.reset":
            _set_status("SETTINGS RESET · sane defaults restored")
        "game.dialogue.auto":
            _set_status("DIALOGUE AUTO · %s" % ("ON" if bool(payload.get("enabled", false)) else "OFF"))
        _:
            _set_status("TYPED INTENT · %s" % intent_id)

func _on_dialogue_visibility_changed(visible: bool) -> void:
    if visible:
        _set_status("VISUAL NOVEL DOCK · GAME PRESENTATION")
    else:
        _set_status("WORLD FIRST · VN DESKTOP · WHISPER · READY")

func _set_status(value: String) -> void:
    if _status_label:
        _status_label.text = value
