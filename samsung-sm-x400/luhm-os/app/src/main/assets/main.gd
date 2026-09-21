extends Node3D

const SPEED := 5.2
const GRAVITY := 18.0
const SAVE_PATH := "user://iron_saint_save.json"

var player: CharacterBody3D
var camera: Camera3D
var automaton: Node3D
var controller: Node3D
var altar: Node3D
var door_left: Node3D
var door_right: Node3D
var touch_move := Vector2.ZERO
var camera_yaw := 0.0
var camera_pitch := -0.05
var awakening_clock := 4
var clues: Array[String] = []
var door_open := false
var won := false

var cockpit: Control
var game_hud: Control
var safe_cockpit: MarginContainer
var safe_game: MarginContainer
var section_title: Label
var section_body: RichTextLabel
var play_button: Button
var status_label: Label
var message_label: Label
var hint_label: Label

const SECTIONS := {
    "authority": ["Authority", "[b]Crown[/b]\nProfessor is final human authority. No AI self-approval.\n\n[b]Boss[/b]\nLum coordinates Context, Build, Research, conditional Critic, and deterministic Tool Executor.\n\n[b]Device contract[/b]\nSamsung SM-X400 · arm64-v8a · no root assumed.\n\n[b]Runtime truth[/b]\nRepository doctrine describes intended state. Device/runtime state requires live evidence."],
    "assets": ["Art & Assets", "[b]Canonical shipping art[/b]\n9 rights-cleared assets are hash-gated in the APK lane.\n\n[b]Private/original art[/b]\nPrivate art remains governed by provenance and publication rules. Third-party private-reference relics are not promoted.\n\n[b]Brand[/b]\nLuHm icon, dark mark, and light mark remain independently hashed."],
    "models": ["3D", "[b]Runtime[/b]\nGodot 4.7.2 stable · GL Compatibility · real Node3D scene.\n\n[b]Current geometry[/b]\nPlayable world uses primitive geometry for the vertical slice. Final character/environment GLB or VRM assets are not falsely claimed.\n\n[b]Rights wall[/b]\nRegistered source references are not equivalent to approved binary models."],
    "roleplay": ["Roleplay Wall", "[b]⚙ Coding Roleplay · ENGINEERING_DSL[/b]\nCompiles only explicit engineering context and still passes Crown, OS, risk, and evidence gates.\n\n[b]║ HARD SEPARATION ║[/b]\n\n[b]🎲 Questforge · FICTIONAL_TABLETOP[/b]\nChanges fictional campaign state only. Zero shell, Git, Android, CI, account, or publishing authority."],
    "questforge": ["Questforge · The Iron Saint", "[b]Hero[/b]\nProfessor Eggie · Level 1 Tinker\n\n[b]Checkpoint[/b]\nBefore the Cathedral Door\n\n[b]Awakening[/b]\n■■■■□□ 4/6\n\n[b]Playable vertical slice[/b]\nInspect the Copper Automaton and KAI-9... controller, open the Cathedral, then reach the Witness Altar.\n\nThe game is fictional state. Entering it does not grant engineering authority."],
    "audit": ["Self Audit", "[b]SOURCE / DOCTRINE[/b] · GREEN\n[b]GODOT3D PACKAGE[/b] · GREEN\n[b]CANONICAL ASSETS[/b] · GREEN\n[b]PERSISTENT UPDATE FORGE[/b] · GREEN\n[b]SM-X400 3D PLAYTEST[/b] · PENDING\n[b]ANDROID 17 RUNTIME[/b] · LATER\n\nEvidence before GREEN. Build success does not imply device success."]
}

func _ready() -> void:
    _build_world()
    _build_player()
    _build_cathedral_cockpit()
    _load_state()
    _apply_door_state()
    _refresh_game_text("Before the Cathedral Door. Find what the Iron Saint remembers.")
    get_viewport().size_changed.connect(_apply_safe_area)
    _apply_safe_area()

func _process(_delta: float) -> void:
    if game_hud != null and game_hud.visible:
        _update_hint()

func _physics_process(delta: float) -> void:
    if game_hud == null or not game_hud.visible:
        return
    var x := 0.0
    var y := 0.0
    if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT): x -= 1.0
    if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT): x += 1.0
    if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP): y -= 1.0
    if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN): y += 1.0
    var axis := Vector2(x, y) + touch_move
    if axis.length() > 1.0: axis = axis.normalized()
    player.rotation.y = camera_yaw
    camera.rotation.x = camera_pitch
    var direction := player.transform.basis * Vector3(axis.x, 0.0, axis.y)
    player.velocity.x = direction.x * SPEED
    player.velocity.z = direction.z * SPEED
    player.velocity.y = player.velocity.y - GRAVITY * delta if not player.is_on_floor() else 0.0
    player.move_and_slide()

func _unhandled_input(event: InputEvent) -> void:
    if game_hud == null or not game_hud.visible:
        return
    if event is InputEventScreenDrag:
        var size := get_viewport().get_visible_rect().size
        if event.position.x > size.x * 0.38:
            camera_yaw -= event.relative.x * 0.005
            camera_pitch = clamp(camera_pitch - event.relative.y * 0.004, -0.65, 0.5)
    elif event is InputEventKey and event.pressed and event.keycode == KEY_E:
        _interact()

func _build_cathedral_cockpit() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(root)

    cockpit = ColorRect.new()
    cockpit.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    cockpit.color = Color(0.025, 0.03, 0.045, 0.96)
    root.add_child(cockpit)

    safe_cockpit = MarginContainer.new()
    safe_cockpit.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    cockpit.add_child(safe_cockpit)
    var app := VBoxContainer.new()
    app.add_theme_constant_override("separation", 12)
    safe_cockpit.add_child(app)

    var header := HBoxContainer.new()
    header.add_theme_constant_override("separation", 18)
    app.add_child(header)
    var brand := VBoxContainer.new()
    brand.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    header.add_child(brand)
    var title := Label.new()
    title.text = "LuHm OS // Cathedral"
    title.add_theme_font_size_override("font_size", 30)
    brand.add_child(title)
    var subtitle := Label.new()
    subtitle.text = "Local cockpit. Canon, art, rights, runtime, and fiction stay separate."
    subtitle.modulate = Color(0.72, 0.78, 0.86)
    brand.add_child(subtitle)
    var badges := VBoxContainer.new()
    badges.add_child(_label("CROWNED SOURCE · GODOT3D · DEVICE PLAYTEST PENDING", 15, Color(0.88, 0.67, 0.3)))
    badges.add_child(_label("SM-X400 · LOCAL ONLY · EVIDENCE BEFORE GREEN", 14, Color(0.55, 0.8, 0.74)))
    header.add_child(badges)

    var body := HBoxContainer.new()
    body.size_flags_vertical = Control.SIZE_EXPAND_FILL
    body.add_theme_constant_override("separation", 14)
    app.add_child(body)

    var nav_panel := PanelContainer.new()
    nav_panel.custom_minimum_size = Vector2(220, 0)
    body.add_child(nav_panel)
    var nav := VBoxContainer.new()
    nav.add_theme_constant_override("separation", 8)
    nav_panel.add_child(nav)
    nav.add_child(_label("Evidence Board", 22, Color(1.0, 0.8, 0.42)))
    nav.add_child(_nav_button("Authority", "authority"))
    nav.add_child(_nav_button("Art & Assets", "assets"))
    nav.add_child(_nav_button("3D", "models"))
    nav.add_child(_nav_button("Roleplay Wall", "roleplay"))
    nav.add_child(_nav_button("Questforge", "questforge"))
    nav.add_child(_nav_button("Self Audit", "audit"))

    var content_panel := PanelContainer.new()
    content_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    body.add_child(content_panel)
    var content := VBoxContainer.new()
    content.add_theme_constant_override("separation", 12)
    content_panel.add_child(content)
    section_title = _label("Authority", 26, Color(0.93, 0.93, 0.98))
    content.add_child(section_title)
    section_body = RichTextLabel.new()
    section_body.bbcode_enabled = true
    section_body.fit_content = false
    section_body.scroll_active = true
    section_body.size_flags_vertical = Control.SIZE_EXPAND_FILL
    section_body.add_theme_font_size_override("normal_font_size", 18)
    section_body.add_theme_font_size_override("bold_font_size", 18)
    content.add_child(section_body)
    play_button = Button.new()
    play_button.text = "ENTER 3D · THE IRON SAINT"
    play_button.custom_minimum_size = Vector2(0, 58)
    play_button.add_theme_font_size_override("font_size", 18)
    play_button.visible = false
    play_button.pressed.connect(_enter_game)
    content.add_child(play_button)

    var receipt_panel := PanelContainer.new()
    receipt_panel.custom_minimum_size = Vector2(300, 0)
    body.add_child(receipt_panel)
    var receipt := VBoxContainer.new()
    receipt.add_theme_constant_override("separation", 10)
    receipt_panel.add_child(receipt)
    receipt.add_child(_label("Truth Receipt", 22, Color(1.0, 0.8, 0.42)))
    receipt.add_child(_label("SOURCE DOCTRINE = CROWNED\nROLEPLAY SYSTEMS = SEPARATED\nCANONICAL APK ASSETS = 9 VERIFIED\n3D RUNTIME = GODOT 4.7.2\nFINAL 3D MODELS = NOT CLAIMED\nUPDATE FORGE = GREEN\nSM-X400 3D PLAYTEST = PENDING\nANDROID 17 = LATER", 15, Color(0.78, 0.84, 0.9)))

    app.add_child(_label("LuHm OS source-of-truth Cathedral · local artifact · runtime claims require evidence", 13, Color(0.55, 0.62, 0.7)))

    game_hud = Control.new()
    game_hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    game_hud.visible = false
    root.add_child(game_hud)
    safe_game = MarginContainer.new()
    safe_game.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    game_hud.add_child(safe_game)
    var game_layout := VBoxContainer.new()
    game_layout.size_flags_vertical = Control.SIZE_EXPAND_FILL
    safe_game.add_child(game_layout)
    var top := VBoxContainer.new()
    game_layout.add_child(top)
    status_label = _label("", 20, Color(1.0, 0.78, 0.36))
    message_label = _label("", 17, Color(0.94, 0.94, 0.96))
    message_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    top.add_child(status_label)
    top.add_child(message_label)
    var spacer := Control.new()
    spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
    game_layout.add_child(spacer)
    var bottom := VBoxContainer.new()
    bottom.add_theme_constant_override("separation", 8)
    game_layout.add_child(bottom)
    hint_label = _label("", 17, Color(0.9, 0.78, 0.48))
    hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    bottom.add_child(hint_label)
    var controls := HBoxContainer.new()
    controls.add_theme_constant_override("separation", 12)
    bottom.add_child(controls)
    var move_pad := GridContainer.new()
    move_pad.columns = 3
    controls.add_child(move_pad)
    move_pad.add_child(_blank_control())
    move_pad.add_child(_move_button("▲", Vector2(0, -1)))
    move_pad.add_child(_blank_control())
    move_pad.add_child(_move_button("◀", Vector2(-1, 0)))
    move_pad.add_child(_move_button("▼", Vector2(0, 1)))
    move_pad.add_child(_move_button("▶", Vector2(1, 0)))
    var control_spacer := Control.new()
    control_spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    controls.add_child(control_spacer)
    var actions := VBoxContainer.new()
    actions.custom_minimum_size = Vector2(210, 0)
    controls.add_child(actions)
    var interact := Button.new()
    interact.text = "INTERACT"
    interact.custom_minimum_size = Vector2(0, 66)
    interact.pressed.connect(_interact)
    actions.add_child(interact)
    var cathedral := Button.new()
    cathedral.text = "CATHEDRAL"
    cathedral.pressed.connect(_return_to_cockpit)
    actions.add_child(cathedral)
    var reset := Button.new()
    reset.text = "RESET SAVE"
    reset.pressed.connect(_reset_game)
    actions.add_child(reset)

    _show_section("authority")

func _label(text: String, size: int, color: Color) -> Label:
    var label := Label.new()
    label.text = text
    label.modulate = color
    label.add_theme_font_size_override("font_size", size)
    return label

func _nav_button(text: String, id: String) -> Button:
    var button := Button.new()
    button.text = text
    button.custom_minimum_size = Vector2(0, 46)
    button.pressed.connect(_show_section.bind(id))
    return button

func _show_section(id: String) -> void:
    var data: Array = SECTIONS[id]
    section_title.text = str(data[0])
    section_body.text = str(data[1])
    play_button.visible = id == "questforge"

func _enter_game() -> void:
    touch_move = Vector2.ZERO
    cockpit.visible = false
    game_hud.visible = true
    _refresh_game_text("Before the Cathedral Door. Find what the Iron Saint remembers.")

func _return_to_cockpit() -> void:
    touch_move = Vector2.ZERO
    game_hud.visible = false
    cockpit.visible = true
    _show_section("questforge")

func _apply_safe_area() -> void:
    var viewport_size := get_viewport().get_visible_rect().size
    var safe := DisplayServer.get_display_safe_area()
    var left := 18.0
    var top := 18.0
    var right := 18.0
    var bottom := 18.0
    if safe.size.x > 0 and safe.size.y > 0 and viewport_size.x > 0 and viewport_size.y > 0:
        left = max(18.0, float(safe.position.x))
        top = max(18.0, float(safe.position.y))
        right = max(18.0, viewport_size.x - float(safe.end.x))
        bottom = max(18.0, viewport_size.y - float(safe.end.y))
    for margin in [safe_cockpit, safe_game]:
        margin.add_theme_constant_override("margin_left", int(left))
        margin.add_theme_constant_override("margin_top", int(top))
        margin.add_theme_constant_override("margin_right", int(right))
        margin.add_theme_constant_override("margin_bottom", int(bottom))

func _move_button(text: String, direction: Vector2) -> Button:
    var button := Button.new()
    button.text = text
    button.custom_minimum_size = Vector2(78, 64)
    button.add_theme_font_size_override("font_size", 22)
    button.button_down.connect(_set_touch_move.bind(direction))
    button.button_up.connect(_clear_touch_move.bind(direction))
    return button

func _blank_control() -> Control:
    var control := Control.new()
    control.custom_minimum_size = Vector2(78, 64)
    return control

func _set_touch_move(direction: Vector2) -> void:
    touch_move += direction
    if touch_move.length() > 1.0: touch_move = touch_move.normalized()

func _clear_touch_move(direction: Vector2) -> void:
    touch_move -= direction
    if touch_move.length() < 0.05: touch_move = Vector2.ZERO

func _build_world() -> void:
    var env_node := WorldEnvironment.new()
    var env := Environment.new()
    env.background_mode = Environment.BG_COLOR
    env.background_color = Color(0.012, 0.018, 0.028, 1.0)
    env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color = Color(0.16, 0.19, 0.24, 1.0)
    env.ambient_light_energy = 0.7
    env.fog_enabled = true
    env.fog_light_color = Color(0.11, 0.13, 0.16, 1.0)
    env.fog_density = 0.018
    env_node.environment = env
    add_child(env_node)
    var moon := DirectionalLight3D.new()
    moon.light_color = Color(0.55, 0.66, 0.86, 1.0)
    moon.light_energy = 1.0
    moon.rotation_degrees = Vector3(-48.0, -30.0, 0.0)
    add_child(moon)
    _box("Floor", Vector3(0, -0.3, -8), Vector3(18, 0.6, 36), Color(0.12, 0.13, 0.14), true)
    _box("LeftWall", Vector3(-8.7, 3.0, -8), Vector3(0.6, 6.0, 36), Color(0.08, 0.09, 0.1), true)
    _box("RightWall", Vector3(8.7, 3.0, -8), Vector3(0.6, 6.0, 36), Color(0.08, 0.09, 0.1), true)
    _box("DoorWallLeft", Vector3(-6.0, 3.0, -12.0), Vector3(5.4, 6.0, 0.7), Color(0.09, 0.09, 0.1), true)
    _box("DoorWallRight", Vector3(6.0, 3.0, -12.0), Vector3(5.4, 6.0, 0.7), Color(0.09, 0.09, 0.1), true)
    _box("RearWall", Vector3(0, 3.0, -25.4), Vector3(18, 6.0, 0.7), Color(0.07, 0.075, 0.09), true)
    for z in [5.0, 1.0, -3.0, -7.0, -15.5, -19.5, -23.0]:
        _column(Vector3(-5.7, 0.0, z)); _column(Vector3(5.7, 0.0, z))
    for z in [4.0, -4.0, -16.0, -22.0]:
        var light := OmniLight3D.new()
        light.position = Vector3(0, 4.6, z)
        light.light_color = Color(1.0, 0.48, 0.18, 1.0)
        light.light_energy = 4.0
        light.omni_range = 11.0
        add_child(light)
    door_left = _box("CathedralDoorLeft", Vector3(-1.5, 2.5, -12.0), Vector3(3.0, 5.0, 0.65), Color(0.22, 0.12, 0.055), true)
    door_right = _box("CathedralDoorRight", Vector3(1.5, 2.5, -12.0), Vector3(3.0, 5.0, 0.65), Color(0.22, 0.12, 0.055), true)
    _add_rune(Vector3(0, 3.0, -11.6), "☩⚙︎  THE IRON SAINT")
    automaton = Node3D.new(); automaton.name = "CopperAutomaton"; automaton.position = Vector3(3.0, 0.0, -5.2); add_child(automaton)
    _primitive_cylinder(automaton, Vector3(0, 1.05, 0), 0.55, 1.65, Color(0.42, 0.22, 0.08))
    _primitive_sphere(automaton, Vector3(0, 2.05, 0), 0.48, Color(0.72, 0.63, 0.49))
    controller = _box("KAI9Controller", Vector3(-3.1, 0.55, -5.0), Vector3(1.2, 1.1, 1.2), Color(0.04, 0.3, 0.34), false)
    altar = _box("WitnessAltar", Vector3(0, 0.65, -21.5), Vector3(2.8, 1.3, 2.0), Color(0.18, 0.11, 0.06), true)
    _add_canonical_tapestry("res://cathedral/CURRENT_KAI9000_CATHEDRAL_POSTER.png", Vector3(0, 3.4, -25.0), Vector2(5.8, 3.4), 0.0)
    _add_canonical_tapestry("res://cathedral/CURRENT_LUM_MIDNIGHT_1996_MODEL_SHEET.png", Vector3(8.25, 3.0, -18.0), Vector2(4.0, 4.0), -PI / 2.0)

func _build_player() -> void:
    player = CharacterBody3D.new(); player.name = "ProfessorEggie"; player.position = Vector3(0, 1.0, 7.0)
    var shape_node := CollisionShape3D.new(); var capsule := CapsuleShape3D.new(); capsule.radius = 0.42; capsule.height = 1.8; shape_node.shape = capsule; player.add_child(shape_node); add_child(player)
    camera = Camera3D.new(); camera.position = Vector3(0, 0.62, 0); camera.current = true; camera.fov = 72.0; player.add_child(camera)

func _interact() -> void:
    if won: _refresh_game_text("The Iron Saint is awake. RESET SAVE to play again."); return
    var d_auto := player.global_position.distance_to(automaton.global_position)
    var d_ctrl := player.global_position.distance_to(controller.global_position)
    var d_door := player.global_position.distance_to(Vector3(0, 1.0, -11.0))
    var d_altar := player.global_position.distance_to(altar.global_position)
    var nearest := min(min(d_auto, d_ctrl), min(d_door, d_altar))
    if nearest > 3.2: _refresh_game_text("Nothing close enough to inspect."); return
    if nearest == d_auto: _discover("The automaton recognizes Professor Eggie.", "Professor identified. Primary operator absent for forty-three years.")
    elif nearest == d_ctrl: _discover("The partial controller marking reads KAI-9...", "Modern control logic hums inside antique copper machinery.")
    elif nearest == d_door:
        if door_open: _refresh_game_text("The Cathedral Door stands open. Enter.")
        elif clues.size() >= 2:
            door_open = true; awakening_clock = 6; _apply_door_state(); _save_state(); _refresh_game_text("Crown authority requires a living witness. The doors unlock.")
        else: _refresh_game_text("The door does not answer yet. Inspect the witnesses outside.")
    elif nearest == d_altar:
        if door_open: won = true; _save_state(); _refresh_game_text("WITNESS ACKNOWLEDGED. The Iron Saint wakes. Vertical slice complete.")
        else: _refresh_game_text("You should not be able to reach this altar yet.")

func _discover(clue: String, text: String) -> void:
    if clue not in clues:
        clues.append(clue); awakening_clock = min(awakening_clock + 1, 6); _save_state()
    _refresh_game_text(text)

func _update_hint() -> void:
    if won: hint_label.text = "✓ WITNESS ACKNOWLEDGED"; return
    var candidates := [[player.global_position.distance_to(automaton.global_position), "INTERACT · Copper Automaton"], [player.global_position.distance_to(controller.global_position), "INTERACT · KAI-9... controller"], [player.global_position.distance_to(Vector3(0, 1.0, -11.0)), "INTERACT · Cathedral Door"], [player.global_position.distance_to(altar.global_position), "INTERACT · Witness Altar"]]
    candidates.sort_custom(func(a, b): return a[0] < b[0])
    hint_label.text = candidates[0][1] if candidates[0][0] <= 3.2 else "Drag right side to look · pad/WASD to move"

func _refresh_game_text(message: String) -> void:
    if status_label == null: return
    var clue_text := "none" if clues.is_empty() else str(clues.size()) + "/2 witnesses found"
    var state := "COMPLETE" if won else ("DOOR OPEN" if door_open else "INVESTIGATE")
    status_label.text = "THE IRON SAINT · " + state + " · Awakening " + str(awakening_clock) + "/6 · " + clue_text
    message_label.text = message
    _update_hint()

func _apply_door_state() -> void:
    if door_left == null or door_right == null: return
    door_left.position.x = -4.6 if door_open else -1.5
    door_right.position.x = 4.6 if door_open else 1.5

func _save_state() -> void:
    var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    if f: f.store_string(JSON.stringify({"clock": awakening_clock, "clues": clues, "door_open": door_open, "won": won}))

func _load_state() -> void:
    if not FileAccess.file_exists(SAVE_PATH): return
    var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
    if not f: return
    var data = JSON.parse_string(f.get_as_text())
    if typeof(data) != TYPE_DICTIONARY: return
    awakening_clock = int(data.get("clock", 4)); clues.clear()
    for clue in data.get("clues", []): clues.append(str(clue))
    door_open = bool(data.get("door_open", false)); won = bool(data.get("won", false))

func _reset_game() -> void:
    if FileAccess.file_exists(SAVE_PATH): DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
    get_tree().reload_current_scene()

func _box(name: String, pos: Vector3, size: Vector3, color: Color, collision: bool) -> Node3D:
    var root: Node3D = StaticBody3D.new() if collision else Node3D.new(); root.name = name; root.position = pos; add_child(root)
    var mesh_node := MeshInstance3D.new(); var mesh := BoxMesh.new(); mesh.size = size; mesh.material = _material(color); mesh_node.mesh = mesh; root.add_child(mesh_node)
    if collision:
        var shape_node := CollisionShape3D.new(); var shape := BoxShape3D.new(); shape.size = size; shape_node.shape = shape; root.add_child(shape_node)
    return root

func _column(pos: Vector3) -> void:
    var body := StaticBody3D.new(); body.position = pos; add_child(body)
    var mesh_node := MeshInstance3D.new(); var mesh := CylinderMesh.new(); mesh.top_radius = 0.55; mesh.bottom_radius = 0.72; mesh.height = 5.5; mesh.material = _material(Color(0.16, 0.14, 0.12)); mesh_node.position.y = 2.75; mesh_node.mesh = mesh; body.add_child(mesh_node)
    var shape_node := CollisionShape3D.new(); var shape := CylinderShape3D.new(); shape.radius = 0.7; shape.height = 5.5; shape_node.position.y = 2.75; shape_node.shape = shape; body.add_child(shape_node)

func _primitive_cylinder(parent: Node3D, pos: Vector3, radius: float, height: float, color: Color) -> void:
    var node := MeshInstance3D.new(); var mesh := CylinderMesh.new(); mesh.top_radius = radius * 0.88; mesh.bottom_radius = radius; mesh.height = height; mesh.material = _material(color); node.position = pos; node.mesh = mesh; parent.add_child(node)

func _primitive_sphere(parent: Node3D, pos: Vector3, radius: float, color: Color) -> void:
    var node := MeshInstance3D.new(); var mesh := SphereMesh.new(); mesh.radius = radius; mesh.height = radius * 2.0; mesh.material = _material(color); node.position = pos; node.mesh = mesh; parent.add_child(node)

func _material(color: Color) -> StandardMaterial3D:
    var mat := StandardMaterial3D.new(); mat.albedo_color = color; mat.metallic = 0.35; mat.roughness = 0.65; return mat

func _add_rune(pos: Vector3, text: String) -> void:
    var label := Label3D.new(); label.text = text; label.position = pos; label.font_size = 34; label.modulate = Color(1.0, 0.7, 0.3, 1.0); label.outline_size = 8; add_child(label)

func _add_canonical_tapestry(path: String, pos: Vector3, size: Vector2, yaw: float) -> void:
    var img := Image.new()
    if img.load(path) != OK: return
    var tex := ImageTexture.create_from_image(img); var quad := QuadMesh.new(); quad.size = size
    var mat := StandardMaterial3D.new(); mat.albedo_texture = tex; mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED; mat.cull_mode = BaseMaterial3D.CULL_DISABLED; quad.material = mat
    var node := MeshInstance3D.new(); node.mesh = quad; node.position = pos; node.rotation.y = yaw; add_child(node)
