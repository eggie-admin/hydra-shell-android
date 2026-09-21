extends Node3D

# LuHm OS world-first Godot HUD controller.
# Presentation state only. No shell, no network, no privilege bridge.

@onready var cockpit: Control = $HUD/HUDRoot/CockpitOverlay
@onready var micro_menu: Control = $HUD/HUDRoot/MicroMenu
@onready var context_button: Button = $HUD/HUDRoot/ContextAction
@onready var quest_label: Label = $HUD/HUDRoot/QuestSigil
@onready var lum_bubble: Button = $HUD/HUDRoot/LumBubble
@onready var lum_guide: Node3D = $World3D/LumGuide
@onready var shrine: MeshInstance3D = $World3D/Shrine

var nearby_action := "EXPLORE"
var session_id := ""
var orbit_phase := 0.0

func _ready() -> void:
    session_id = "%s-%s" % [Time.get_unix_time_from_system(), randi_range(1000, 9999)]
    cockpit.visible = false
    micro_menu.visible = false
    _sync_hud()

func _process(delta: float) -> void:
    orbit_phase += delta
    lum_guide.position.y = 1.3 + sin(orbit_phase * 1.8) * 0.08
    shrine.rotation.y += delta * 0.22

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("ui_cancel"):
        if cockpit.visible:
            cockpit.visible = false
            get_viewport().set_input_as_handled()
        elif micro_menu.visible:
            micro_menu.visible = false
            get_viewport().set_input_as_handled()

func set_context_action(action_name: String) -> void:
    nearby_action = action_name.to_upper()
    _sync_hud()

func _sync_hud() -> void:
    context_button.text = nearby_action
    if not quest_label.text.begins_with("◇"):
        quest_label.text = "◇ CORKTOWN"

func _on_lum_bubble_pressed() -> void:
    micro_menu.visible = not micro_menu.visible
    cockpit.visible = false

func _on_cockpit_pressed() -> void:
    micro_menu.visible = false
    cockpit.visible = true

func _on_cockpit_close_pressed() -> void:
    cockpit.visible = false

func _on_context_action_pressed() -> void:
    match nearby_action:
        "CONTACT":
            quest_label.text = "◇ CONTACT READY"
        "FUSION":
            quest_label.text = "◇ SHRINE RESONANCE"
        "SAVEPOINT":
            quest_label.text = "◇ SAVEPOINT"
        _:
            quest_label.text = "◇ EXPLORE"
