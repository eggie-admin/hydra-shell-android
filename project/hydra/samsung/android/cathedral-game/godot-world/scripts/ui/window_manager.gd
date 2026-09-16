extends Control
class_name LuHmWindowManager

signal window_opened(window_id: String)
signal window_closed(window_id: String)

var _windows: Dictionary = {}
var _handles: Dictionary = {}
var _drag_id := ""
var _drag_offset := Vector2.ZERO
var _z_counter := 30

func register_window(window_id: String, window: Control, drag_handle: Control = null) -> void:
    _windows[window_id] = window
    _handles[window_id] = drag_handle
    window.visible = false
    if drag_handle:
        drag_handle.gui_input.connect(_on_drag_input.bind(window_id))
    window.gui_input.connect(_on_window_input.bind(window_id))

func open_window(window_id: String) -> void:
    var window: Control = _windows.get(window_id)
    if not window:
        return
    focus_window(window_id)
    window.visible = true
    _snap_inside(window)
    emit_signal("window_opened", window_id)

func close_window(window_id: String) -> void:
    var window: Control = _windows.get(window_id)
    if not window:
        return
    window.visible = false
    if _drag_id == window_id:
        _drag_id = ""
    emit_signal("window_closed", window_id)

func toggle_window(window_id: String) -> void:
    var window: Control = _windows.get(window_id)
    if not window:
        return
    if window.visible:
        close_window(window_id)
    else:
        open_window(window_id)

func focus_window(window_id: String) -> void:
    var window: Control = _windows.get(window_id)
    if not window:
        return
    _z_counter += 1
    window.z_index = _z_counter

func close_all() -> void:
    for window_id in _windows.keys():
        close_window(String(window_id))

func _on_window_input(event: InputEvent, window_id: String) -> void:
    if event is InputEventMouseButton and event.pressed:
        focus_window(window_id)
    elif event is InputEventScreenTouch and event.pressed:
        focus_window(window_id)

func _on_drag_input(event: InputEvent, window_id: String) -> void:
    var window: Control = _windows.get(window_id)
    if not window:
        return

    if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed:
            focus_window(window_id)
            _drag_id = window_id
            _drag_offset = event.global_position - window.global_position
        elif _drag_id == window_id:
            _drag_id = ""
            _snap_inside(window)
        return

    if event is InputEventMouseMotion and _drag_id == window_id:
        window.global_position = event.global_position - _drag_offset
        return

    if event is InputEventScreenTouch:
        if event.pressed:
            focus_window(window_id)
            _drag_id = window_id
            _drag_offset = event.position - window.global_position
        elif _drag_id == window_id:
            _drag_id = ""
            _snap_inside(window)
        return

    if event is InputEventScreenDrag and _drag_id == window_id:
        window.global_position = event.position - _drag_offset

func _snap_inside(window: Control) -> void:
    var viewport_size := get_viewport_rect().size
    var margin := 12.0
    var max_x := max(margin, viewport_size.x - window.size.x - margin)
    var max_y := max(margin, viewport_size.y - window.size.y - margin)
    window.position.x = clamp(window.position.x, margin, max_x)
    window.position.y = clamp(window.position.y, margin, max_y)
