extends Node3D

# LuHm OS world-first Godot HUD controller.
# Presentation state only. No shell, no network, no privilege bridge.

@onready var cockpit: Control = $HUD/CockpitOverlay
@onready var micro_menu: Control = $HUD/MicroMenu
@onready var context_label: Label = $HUD/ContextAction/Label
@onready var quest_label: Label = $HUD/QuestSigil/Label
@onready var lum_bubble: Button = $HUD/LumBubble

var nearby_action := "EXPLORE"
var session_id := ""

func _ready() -> void:
    session_id = str(Time.get_unix_time_from_system())
    cockpit.visible = false
    micro_menu.visible = false
    _sync_hud()

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
    context_label.text = nearby_action
    quest_label.text = "◇ CORKTOWN"

func _on_lum_bubble_pressed() -> void:
    micro_menu.visible = not micro_menu.visible
    cockpit.visible = false

func _on_cockpit_pressed() -> void:
    micro_menu.visible = false
    cockpit.visible = true

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
