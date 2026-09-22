extends Node3D

# LUHM_NATIVE_3D_HARNESS_V1
# Native Godot world stays underneath the web Cathedral tier. World mode hides
# the Android WebView and exposes this scene plus a small native return dock.

signal avatar_state_changed(state: StringName)

const PLUGIN_NAME := "CathedralAndroid"

var avatar_state: StringName = &"idle"
var _plugin = null
var _bridge: Node = null
var _world_hud: CanvasLayer = null
var _world_active := false
var _lum_marker: Node3D = null

func _ready() -> void:
    get_window().gui_embed_subwindows = true
    if OS.get_name() == "Android" and Engine.has_singleton(PLUGIN_NAME):
        _plugin = Engine.get_singleton(PLUGIN_NAME)
    _bridge = get_node_or_null("WebCmsBridge")
    _build_world()
    _build_world_hud()
    set_avatar_state(&"idle")

func _process(delta: float) -> void:
    if _lum_marker:
        _lum_marker.rotate_y(delta * 0.35)

func _notification(what: int) -> void:
    if what == NOTIFICATION_WM_GO_BACK_REQUEST and _world_active:
        exit_world_mode()

func set_avatar_state(next_state: StringName) -> void:
    avatar_state = next_state
    avatar_state_changed.emit(avatar_state)

func open_tool_window(title: String, size := Vector2i(520, 360)) -> Window:
    var window := Window.new()
    window.title = title
    window.size = size
    window.transient = false
    window.exclusive = false
    add_child(window)
    window.popup_centered()
    return window

func enter_world_mode() -> void:
    _world_active = true
    if _world_hud:
        _world_hud.visible = true
    if _bridge and _bridge.has_method("close_cms"):
        _bridge.close_cms()
    if _plugin and _plugin.has_method("setImmersiveKiosk"):
        _plugin.setImmersiveKiosk(true)

func exit_world_mode() -> void:
    _world_active = false
    if _world_hud:
        _world_hud.visible = false
    if _bridge and _bridge.has_method("open_cms"):
        _bridge.open_cms()

func _open_web_tier(panel: String) -> void:
    exit_world_mode()
    await get_tree().create_timer(0.08).timeout
    if _bridge and _bridge.has_method("send_to_cms"):
        _bridge.send_to_cms({"type": "host.ui.open", "payload": {"panel": panel}})

func _build_world() -> void:
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("#080710")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("#6e4a8e")
    environment.ambient_light_energy = 0.9

    var world_environment := WorldEnvironment.new()
    world_environment.environment = environment
    add_child(world_environment)

    var key_light := DirectionalLight3D.new()
    key_light.rotation_degrees = Vector3(-48.0, -28.0, 0.0)
    key_light.light_color = Color("#f1d8ff")
    key_light.light_energy = 1.35
    key_light.shadow_enabled = true
    add_child(key_light)

    var floor_mesh := PlaneMesh.new()
    floor_mesh.size = Vector2(70.0, 70.0)
    var floor_material := StandardMaterial3D.new()
    floor_material.albedo_color = Color("#0a0812")
    floor_material.metallic = 0.45
    floor_material.roughness = 0.32
    floor_mesh.material = floor_material
    var floor := MeshInstance3D.new()
    floor.mesh = floor_mesh
    add_child(floor)

    for row in range(5):
        for col in range(-5, 6):
            var height := 1.8 + float(abs(col * 7 + row * 11) % 6)
            var box_mesh := BoxMesh.new()
            box_mesh.size = Vector3(2.2, height, 2.2)
            var box_material := StandardMaterial3D.new()
            box_material.albedo_color = Color("#151022")
            box_material.metallic = 0.25
            box_material.roughness = 0.5
            box_material.emission_enabled = true
            box_material.emission = Color("#2d1745") if (col + row) % 2 == 0 else Color("#103448")
            box_mesh.material = box_material
            var tower := MeshInstance3D.new()
            tower.mesh = box_mesh
            tower.position = Vector3(float(col) * 3.3, height * 0.5, -7.0 - float(row) * 4.0)
            add_child(tower)

    var marker_mesh := SphereMesh.new()
    marker_mesh.radius = 0.85
    marker_mesh.height = 1.7
    var marker_material := StandardMaterial3D.new()
    marker_material.albedo_color = Color("#ff4b88")
    marker_material.emission_enabled = true
    marker_material.emission = Color("#8a5cff")
    marker_mesh.material = marker_material
    var marker := MeshInstance3D.new()
    marker.mesh = marker_mesh
    marker.position = Vector3(0.0, 2.2, -4.0)
    add_child(marker)
    _lum_marker = marker

    var marker_light := OmniLight3D.new()
    marker_light.position = Vector3(0.0, 2.5, -4.0)
    marker_light.light_color = Color("#ff5ea8")
    marker_light.light_energy = 3.0
    marker_light.omni_range = 8.0
    add_child(marker_light)

    var camera := Camera3D.new()
    camera.position = Vector3(0.0, 5.8, 14.0)
    add_child(camera)
    camera.look_at(Vector3(0.0, 2.0, -9.0), Vector3.UP)
    camera.current = true

func _build_world_hud() -> void:
    _world_hud = CanvasLayer.new()
    _world_hud.layer = 50
    add_child(_world_hud)

    var margin := MarginContainer.new()
    margin.set_anchors_preset(Control.PRESET_TOP_WIDE)
    margin.offset_left = 14.0
    margin.offset_top = 14.0
    margin.offset_right = -14.0
    margin.offset_bottom = 104.0
    _world_hud.add_child(margin)

    var panel := PanelContainer.new()
    margin.add_child(panel)

    var stack := VBoxContainer.new()
    panel.add_child(stack)

    var title := Label.new()
    title.text = "LUHM WORLD // NATIVE 3D RUNTIME"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    stack.add_child(title)

    var row := HBoxContainer.new()
    row.alignment = BoxContainer.ALIGNMENT_CENTER
    stack.add_child(row)

    _add_world_button(row, "CATHEDRAL", "cathedral")
    _add_world_button(row, "SYSTEM", "system")
    _add_world_button(row, "COCKPIT", "admin")
    _add_world_button(row, "LUM", "lum")

    var status := Label.new()
    status.text = "Godot 3D tier active · Android WebView tier hidden · BACK returns to Cathedral"
    status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    stack.add_child(status)

    _world_hud.visible = false

func _add_world_button(parent: Control, text: String, action: String) -> void:
    var button := Button.new()
    button.text = text
    button.custom_minimum_size = Vector2(120.0, 42.0)
    button.pressed.connect(_on_world_button.bind(action))
    parent.add_child(button)

func _on_world_button(action: String) -> void:
    match action:
        "cathedral":
            exit_world_mode()
        "system":
            _open_web_tier("system")
        "admin":
            _open_web_tier("admin")
        "lum":
            _open_web_tier("lum")
