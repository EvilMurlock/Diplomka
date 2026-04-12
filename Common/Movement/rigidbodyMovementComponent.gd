extends Node
class_name RigidbodyMovementComponent

@export var movementInput:Vector2Container

var body:RigidBody2D

var acceleration:float = 40
var movementDir:Vector2 = Vector2.ZERO
var movement_locked:Array[Node] = []

func _ready():

	body = $".."
	if 1 != multiplayer.get_unique_id():
		set_process(false)
		set_physics_process(false)
	
func _physics_process(delta: float) -> void:

	updateMovementDirection()
	if movement_locked.size() == 0:
		body.apply_impulse(movementDir.normalized()*acceleration) # already applies delta internaly

		
func updateMovementDirection():
	movementDir = movementInput.value	
