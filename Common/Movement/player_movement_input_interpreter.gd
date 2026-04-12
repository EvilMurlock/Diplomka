extends Node
class_name PlayerMovementInputInterpreter

@export var movementContainer:Vector2Container
@export var player:Node
func _ready() -> void:
	
	if int(player.name) != multiplayer.get_unique_id():
		set_process(false)
		set_physics_process(false)
	read_input()
		
func _process(delta: float) -> void:
	read_input()
	
func read_input() -> void:
	var movementDir = Vector2.ZERO
	
	var left = Input.is_action_pressed("MoveLeft")
	var right = Input.is_action_pressed("MoveRight")
	var up = Input.is_action_pressed("MoveUp")
	var down = Input.is_action_pressed("MoveDown")
	
	movementDir += Vector2.LEFT*int(left)
	movementDir += Vector2.RIGHT*int(right)
	movementDir += Vector2.UP*int(up)
	movementDir += Vector2.DOWN*int(down)

	movementContainer.value = movementDir
