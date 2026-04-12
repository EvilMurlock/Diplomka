extends Node
class_name FacingComponent

var movementComponent:RigidbodyMovementComponent
var facing:Vector2 = Vector2.UP

func _ready() -> void:
	movementComponent = $".."
	
func _process(delta: float) -> void:
	if movementComponent.movementDir != Vector2.ZERO:
		facing = movementComponent.movementDir.normalized()
