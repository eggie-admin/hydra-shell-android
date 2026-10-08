extends Node3D

# LuHm OS world-first Godot HUD controller.
# Presentation state only. No shell, no network, no privilege bridge.
# 1.0.8 candidate adds a local-only physical proof harness.

const SAVE_PATH := "user://luhmos_physical_proof.cfg"

@onready var cockpit: Control = $HUD/HUDRoot/CockpitOverlay
@onready var micro_menu: Control = $HUD/HUDRoot/MicroMenu
@onready var context_button: Button = $HUD/HUDRoot/ContextAction
@onready var quest_label: Label = $HUD/HUDRoot/QuestSigil
@onready var status_label: Label = $HUD/HUDRoot/StatusSigils
@onready var lum_bubble: Button = $HUD/HUDRoot/LumBubble
@onready var proof_label: Label = $HUD/HUDRoot/CockpitOverlay/VBox/ProofState
@onready var lum_guide: Node3D = $World3D/LumGuide
@onready var shrine: MeshInstance3D = $World3D/Shrine

var nearby_action := "EXPLORE"
var session_id := ""
var orbit_phase := 0.0
var ui_mode := "SPRITE_BUBBLE"
var realm := "GAME"
var proof_counter := 0
var last_saved_session := "NONE"

func _ready() -> void:
    session_id = "%s-%s" % [Time.get_unix_time_from_system(), randi_range(1000, 9999)]
    cockpit.visible = false
    micro_menu.visible = false
    _load_proof_state()
    _sync_hud()

func _process(delta: float) -> void:
    orbit_phase += delta
    lum_guide.position.y = 1.3 + sin(orbit_phase * 1.8) * 0.08
    shrine.rotation.y += delta * 0.22

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("ui_cancel"):
        if cockpit.visible:
            cockpit.visible = false
            micro_menu.visible = false
            ui_mode = "SPRITE_BUBBLE"
            realm = "GAME"
            _sync_hud()
            get_viewport().set_input_as_handled()
        elif micro_menu.visible:
            micro_menu.visible = false
            ui_mode = "SPRITE_BUBBLE"
            realm = "GAME"
            _sync_hud()
            get_viewport().set_input_as_handled()

func set_context_action(action_name: String) -> void:
    nearby_action = action_name.to_upper()
    _sync_hud()

func _sync_hud() -> void:
    context_button.text = nearby_action
    if not quest_label.text.begins_with("◇"):
        quest_label.text = "◇ CORKTOWN"
    status_label.text = "♡  ◈  %s" % realm
    proof_label.text = "PHYSICAL PROOF HARNESS\nMODE: %s\nREALM: %s\nSESSION: %s\nSAVEPOINT: %d\nRESTORED SESSION: %s" % [ui_mode, realm, session_id, proof_counter, last_saved_session]

func _load_proof_state() -> void:
    var cfg := ConfigFile.new()
    var err := cfg.load(SAVE_PATH)
    if err == OK:
        proof_counter = int(cfg.get_value("proof", "counter", 0))
        last_saved_session = str(cfg.get_value("proof", "session_id", "NONE"))

func _save_proof_state() -> void:
    proof_counter += 1
    var cfg := ConfigFile.new()
    cfg.set_value("proof", "counter", proof_counter)
    cfg.set_value("proof", "session_id", session_id)
    cfg.set_value("proof", "realm", realm)
    cfg.set_value("proof", "mode", ui_mode)
    var err := cfg.save(SAVE_PATH)
    if err == OK:
        last_saved_session = session_id
        quest_label.text = "◇ SAVEPOINT %d SEALED" % proof_counter
    else:
        quest_label.text = "◇ SAVEPOINT WRITE ERROR %d" % err
    _sync_hud()

func _set_realm(next_realm: String) -> void:
    realm = next_realm
    _sync_hud()

func _on_lum_bubble_pressed() -> void:
    micro_menu.visible = not micro_menu.visible
    cockpit.visible = false
    ui_mode = "WIDGET_DECK" if micro_menu.visible else "SPRITE_BUBBLE"
    realm = "GAME"
    _sync_hud()

func _on_cockpit_pressed() -> void:
    micro_menu.visible = false
    cockpit.visible = true
    ui_mode = "FULL_COCKPIT"
    realm = "ADMIN"
    _sync_hud()

func _on_cockpit_close_pressed() -> void:
    cockpit.visible = false
    micro_menu.visible = false
    ui_mode = "SPRITE_BUBBLE"
    realm = "GAME"
    _sync_hud()

func _on_realm_game_pressed() -> void:
    _set_realm("GAME")

func _on_realm_admin_pressed() -> void:
    _set_realm("ADMIN")

func _on_realm_system_pressed() -> void:
    _set_realm("SYSTEM")

func _on_context_action_pressed() -> void:
    match nearby_action:
        "CONTACT":
            quest_label.text = "◇ CONTACT READY"
        "FUSION":
            quest_label.text = "◇ SHRINE RESONANCE"
        "SAVEPOINT":
            _save_proof_state()
            return
        _:
            quest_label.text = "◇ EXPLORE"
    _sync_hud()
