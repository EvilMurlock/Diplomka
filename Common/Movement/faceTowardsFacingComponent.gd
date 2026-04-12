extends Node
class_name FaceTowardsFacingComponent

@export var facingComponent:FacingComponent
@export var centre:Node2D
@export var radius:float = 0
var target:Node2D

func _ready() -> void:
	target = $".."

func _process(delta: float) -> void:
	target.global_position = centre.global_position + facingComponent.facing * radius
	target.look_at(target.global_position + facingComponent.facing)
