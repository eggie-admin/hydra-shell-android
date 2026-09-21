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
var message_label: Label
var status_label: Label
var hint_label: Label
var touch_move := Vector2.ZERO
var camera_yaw := 0.0
var camera_pitch := -0.05
var awakening_clock := 4
var clues: Array[String] = []
var door_open := false
var won := false

func _ready() -> void:
    _build_world()
    _build_player()
    _build_hud()
    _load_state()
    _apply_door_state()
    _update_status()
    message_label.text = "Before the Cathedral Door. Find what the Iron Saint remembers."

func _process(_delta: float) -> void:
    _update_hint()

func _physics_process(delta: float) -> void:
    var x := 0.0
    var y := 0.0
    if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT): x -= 1.0
    if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT): x += 1.0
    if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP): y -= 1.0
    if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN): y += 1.0
    var axis := Vector2(x, y) + touch_move
    if axis.length() > 1.0:
        axis = axis.normalized()

    player.rotation.y = camera_yaw
    camera.rotation.x = camera_pitch
    var direction := player.transform.basis * Vector3(axis.x, 0.0, axis.y)
    player.velocity.x = direction.x * SPEED
    player.velocity.z = direction.z * SPEED
    if not player.is_on_floor():
        player.velocity.y -= GRAVITY * delta
    else:
        player.velocity.y = 0.0
    player.move_and_slide()

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventScreenDrag:
        var size := get_viewport().get_visible_rect().size
        if event.position.x > size.x * 0.38:
            camera_yaw -= event.relative.x * 0.005
            camera_pitch = clamp(camera_pitch - event.relative.y * 0.004, -0.65, 0.5)
    elif event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
        camera_yaw -= event.relative.x * 0.003
        camera_pitch = clamp(camera_pitch - event.relative.y * 0.003, -0.65, 0.5)
    elif event is InputEventMouseButton and event.pressed:
        Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
    elif event is InputEventKey and event.pressed and event.keycode == KEY_E:
        _interact()

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
        _column(Vector3(-5.7, 0.0, z))
        _column(Vector3(5.7, 0.0, z))

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

    automaton = Node3D.new()
    automaton.name = "CopperAutomaton"
    automaton.position = Vector3(3.0, 0.0, -5.2)
    add_child(automaton)
    _primitive_cylinder(automaton, Vector3(0, 1.05, 0), 0.55, 1.65, Color(0.42, 0.22, 0.08))
    _primitive_sphere(automaton, Vector3(0, 2.05, 0), 0.48, Color(0.72, 0.63, 0.49))
    _primitive_sphere(automaton, Vector3(-0.17, 2.12, -0.43), 0.055, Color(1.0, 0.52, 0.08), true)
    _primitive_sphere(automaton, Vector3(0.17, 2.12, -0.43), 0.055, Color(1.0, 0.52, 0.08), true)
    _add_rune(automaton.position + Vector3(0, 2.9, 0), "COPPER AUTOMATON")

    controller = _box("KAI9Controller", Vector3(-3.1, 0.55, -5.0), Vector3(1.2, 1.1, 1.2), Color(0.04, 0.3, 0.34), false)
    _add_rune(controller.position + Vector3(0, 1.3, 0), "KAI-9...")

    altar = _box("WitnessAltar", Vector3(0, 0.65, -21.5), Vector3(2.8, 1.3, 2.0), Color(0.18, 0.11, 0.06), true)
    _add_rune(Vector3(0, 2.0, -21.5), "WITNESS ALTAR")

    _add_canonical_tapestry("res://cathedral/CURRENT_KAI9000_CATHEDRAL_POSTER.png", Vector3(0, 3.4, -25.0), Vector2(5.8, 3.4), 0.0)
    _add_canonical_tapestry("res://cathedral/CURRENT_LUM_MIDNIGHT_1996_MODEL_SHEET.png", Vector3(8.25, 3.0, -18.0), Vector2(4.0, 4.0), -PI / 2.0)

func _build_player() -> void:
    player = CharacterBody3D.new()
    player.name = "ProfessorEggie"
    player.position = Vector3(0, 1.0, 7.0)
    var shape_node := CollisionShape3D.new()
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.42
    capsule.height = 1.8
    shape_node.shape = capsule
    player.add_child(shape_node)
    add_child(player)

    camera = Camera3D.new()
    camera.position = Vector3(0, 0.62, 0)
    camera.current = true
    camera.fov = 72.0
    player.add_child(camera)

func _build_hud() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(root)

    status_label = Label.new()
    status_label.position = Vector2(20, 18)
    status_label.size = Vector2(720, 95)
    status_label.add_theme_font_size_override("font_size", 22)
    root.add_child(status_label)

    message_label = Label.new()
    message_label.position = Vector2(20, 110)
    message_label.size = Vector2(850, 80)
    message_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    message_label.add_theme_font_size_override("font_size", 18)
    root.add_child(message_label)

    hint_label = Label.new()
    hint_label.anchor_left = 0.5
    hint_label.anchor_right = 0.5
    hint_label.anchor_top = 1.0
    hint_label.anchor_bottom = 1.0
    hint_label.offset_left = -260
    hint_label.offset_right = 260
    hint_label.offset_top = -92
    hint_label.offset_bottom = -52
    hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    hint_label.add_theme_font_size_override("font_size", 18)
    root.add_child(hint_label)

    var up := _hud_button(root, "▲", 118, -208, 86, 66)
    var left := _hud_button(root, "◀", 22, -132, 86, 66)
    var down := _hud_button(root, "▼", 118, -132, 86, 66)
    var right := _hud_button(root, "▶", 214, -132, 86, 66)
    up.button_down.connect(_set_move.bind("y", -1.0)); up.button_up.connect(_set_move.bind("y", 0.0))
    down.button_down.connect(_set_move.bind("y", 1.0)); down.button_up.connect(_set_move.bind("y", 0.0))
    left.button_down.connect(_set_move.bind("x", -1.0)); left.button_up.connect(_set_move.bind("x", 0.0))
    right.button_down.connect(_set_move.bind("x", 1.0)); right.button_up.connect(_set_move.bind("x", 0.0))

    var interact := Button.new()
    interact.text = "INTERACT"
    interact.anchor_left = 1.0
    interact.anchor_right = 1.0
    interact.anchor_top = 1.0
    interact.anchor_bottom = 1.0
    interact.offset_left = -190
    interact.offset_right = -24
    interact.offset_top = -128
    interact.offset_bottom = -58
    interact.add_theme_font_size_override("font_size", 19)
    interact.pressed.connect(_interact)
    root.add_child(interact)

    var reset := Button.new()
    reset.text = "RESET SAVE"
    reset.anchor_left = 1.0
    reset.anchor_right = 1.0
    reset.offset_left = -170
    reset.offset_right = -20
    reset.offset_top = 18
    reset.offset_bottom = 62
    reset.pressed.connect(_reset_game)
    root.add_child(reset)

func _hud_button(root: Control, text: String, left: float, top_from_bottom: float, width: float, height: float) -> Button:
    var b := Button.new()
    b.text = text
    b.anchor_top = 1.0
    b.anchor_bottom = 1.0
    b.offset_left = left
    b.offset_right = left + width
    b.offset_top = top_from_bottom
    b.offset_bottom = top_from_bottom + height
    b.add_theme_font_size_override("font_size", 24)
    root.add_child(b)
    return b

func _set_move(axis: String, value: float) -> void:
    if axis == "x":
        touch_move.x = value
    else:
        touch_move.y = value

func _interact() -> void:
    if won:
        message_label.text = "The Iron Saint is awake. RESET SAVE to play the slice again."
        return
    var d_auto := player.global_position.distance_to(automaton.global_position)
    var d_ctrl := player.global_position.distance_to(controller.global_position)
    var d_door := player.global_position.distance_to(Vector3(0, 1.0, -11.0))
    var d_altar := player.global_position.distance_to(altar.global_position)
    var nearest := min(min(d_auto, d_ctrl), min(d_door, d_altar))
    if nearest > 3.2:
        message_label.text = "Nothing close enough to inspect."
        return
    if nearest == d_auto:
        _discover("The automaton recognizes Professor Eggie.", "Professor identified. Primary operator absent for forty-three years.")
    elif nearest == d_ctrl:
        _discover("The partial controller marking reads KAI-9...", "Modern control logic hums inside antique copper machinery.")
    elif nearest == d_door:
        if door_open:
            message_label.text = "The Cathedral Door stands open. Enter."
        elif clues.size() >= 2:
            door_open = true
            awakening_clock = 6
            _apply_door_state()
            _save_state()
            _update_status()
            message_label.text = "Crown authority requires a living witness. The doors unlock."
        else:
            message_label.text = "The door does not answer yet. Inspect the witnesses outside."
    elif nearest == d_altar:
        if door_open:
            won = true
            _save_state()
            _update_status()
            message_label.text = "WITNESS ACKNOWLEDGED. The Iron Saint wakes. Vertical slice complete."
        else:
            message_label.text = "You should not be able to reach this altar yet."

func _discover(clue: String, text: String) -> void:
    if clue not in clues:
        clues.append(clue)
        awakening_clock = min(awakening_clock + 1, 6)
        _save_state()
    _update_status()
    message_label.text = text

func _update_hint() -> void:
    if won:
        hint_label.text = "✓ WITNESS ACKNOWLEDGED"
        return
    var candidates := [
        [player.global_position.distance_to(automaton.global_position), "INTERACT · Copper Automaton"],
        [player.global_position.distance_to(controller.global_position), "INTERACT · KAI-9... controller"],
        [player.global_position.distance_to(Vector3(0, 1.0, -11.0)), "INTERACT · Cathedral Door"],
        [player.global_position.distance_to(altar.global_position), "INTERACT · Witness Altar"]
    ]
    candidates.sort_custom(func(a, b): return a[0] < b[0])
    hint_label.text = candidates[0][1] if candidates[0][0] <= 3.2 else "Drag right side to look · arrows/WASD to move"

func _update_status() -> void:
    var clue_text := "none" if clues.is_empty() else str(clues.size()) + "/2 witnesses found"
    var state := "COMPLETE" if won else ("DOOR OPEN" if door_open else "INVESTIGATE")
    status_label.text = "THE IRON SAINT · " + state + "\nAwakening " + str(awakening_clock) + "/6 · " + clue_text

func _apply_door_state() -> void:
    if door_left == null or door_right == null:
        return
    door_left.position.x = -4.6 if door_open else -1.5
    door_right.position.x = 4.6 if door_open else 1.5

func _save_state() -> void:
    var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    if f:
        f.store_string(JSON.stringify({"clock": awakening_clock, "clues": clues, "door_open": door_open, "won": won}))

func _load_state() -> void:
    if not FileAccess.file_exists(SAVE_PATH):
        return
    var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
    if not f:
        return
    var data = JSON.parse_string(f.get_as_text())
    if typeof(data) != TYPE_DICTIONARY:
        return
    awakening_clock = int(data.get("clock", 4))
    clues.clear()
    for clue in data.get("clues", []):
        clues.append(str(clue))
    door_open = bool(data.get("door_open", false))
    won = bool(data.get("won", false))

func _reset_game() -> void:
    if FileAccess.file_exists(SAVE_PATH):
        DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
    get_tree().reload_current_scene()

func _box(name: String, pos: Vector3, size: Vector3, color: Color, collision: bool) -> Node3D:
    var root: Node3D
    if collision:
        root = StaticBody3D.new()
    else:
        root = Node3D.new()
    root.name = name
    root.position = pos
    add_child(root)
    var mesh_node := MeshInstance3D.new()
    var mesh := BoxMesh.new()
    mesh.size = size
    mesh.material = _material(color)
    mesh_node.mesh = mesh
    root.add_child(mesh_node)
    if collision:
        var shape_node := CollisionShape3D.new()
        var shape := BoxShape3D.new()
        shape.size = size
        shape_node.shape = shape
        root.add_child(shape_node)
    return root

func _column(pos: Vector3) -> void:
    var body := StaticBody3D.new()
    body.position = pos
    add_child(body)
    var mesh_node := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = 0.55
    mesh.bottom_radius = 0.72
    mesh.height = 5.5
    mesh.material = _material(Color(0.16, 0.14, 0.12))
    mesh_node.position.y = 2.75
    mesh_node.mesh = mesh
    body.add_child(mesh_node)
    var shape_node := CollisionShape3D.new()
    var shape := CylinderShape3D.new()
    shape.radius = 0.7
    shape.height = 5.5
    shape_node.position.y = 2.75
    shape_node.shape = shape
    body.add_child(shape_node)

func _primitive_cylinder(parent: Node3D, pos: Vector3, radius: float, height: float, color: Color) -> void:
    var node := MeshInstance3D.new()
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius * 0.88
    mesh.bottom_radius = radius
    mesh.height = height
    mesh.material = _material(color)
    node.position = pos
    node.mesh = mesh
    parent.add_child(node)

func _primitive_sphere(parent: Node3D, pos: Vector3, radius: float, color: Color, emissive := false) -> void:
    var node := MeshInstance3D.new()
    var mesh := SphereMesh.new()
    mesh.radius = radius
    mesh.height = radius * 2.0
    mesh.material = _material(color, emissive)
    node.position = pos
    node.mesh = mesh
    parent.add_child(node)

func _material(color: Color, emissive := false) -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.metallic = 0.35
    mat.roughness = 0.65
    if emissive:
        mat.emission_enabled = true
        mat.emission = color
        mat.emission_energy_multiplier = 4.0
    return mat

func _add_rune(pos: Vector3, text: String) -> void:
    var label := Label3D.new()
    label.text = text
    label.position = pos
    label.font_size = 34
    label.modulate = Color(1.0, 0.7, 0.3, 1.0)
    label.outline_size = 8
    add_child(label)

func _add_canonical_tapestry(path: String, pos: Vector3, size: Vector2, yaw: float) -> void:
    var img := Image.new()
    if img.load(path) != OK:
        return
    var tex := ImageTexture.create_from_image(img)
    var quad := QuadMesh.new()
    quad.size = size
    var mat := StandardMaterial3D.new()
    mat.albedo_texture = tex
    mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    mat.cull_mode = BaseMaterial3D.CULL_DISABLED
    quad.material = mat
    var node := MeshInstance3D.new()
    node.mesh = quad
    node.position = pos
    node.rotation.y = yaw
    add_child(node)
