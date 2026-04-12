extends Node
class_name AttackComponent

@export var hitbox:HitboxComponent
@export var attack_input:BoolContainer
@export var movementComponent:RigidbodyMovementComponent


@export var stop_movement:bool

@export var startup:float
@export var active:float
@export var recovery:float

var attacking = false


func _ready() -> void:
	pass
	print(attack_input.value_changed.connect(start_attack))

func start_attack(attack:bool) -> void:
	if attack == false || attacking:
		return
		
	attacking = true
	if stop_movement:
		movementComponent.movement_locked.append(self)
	
	var timer:SceneTreeTimer = get_tree().create_timer(startup)  
	timer.timeout.connect(startup_active)  
	
func startup_active() -> void:
	hitbox.show()
	hitbox.set_deferred("monitoring", true)
	hitbox.set_deferred("monitorable", true)

	var timer:SceneTreeTimer = get_tree().create_timer(active)  
	timer.timeout.connect(active_recover)  
	
func active_recover() -> void:
	hitbox.hide()
	hitbox.set_deferred("monitoring", false)
	hitbox.set_deferred("monitorable", false)

	var timer:SceneTreeTimer = get_tree().create_timer(recovery)  
	timer.timeout.connect(recovery_end)

func recovery_end() -> void:
	attacking = false
	if stop_movement:
		movementComponent.movement_locked.erase(self)
