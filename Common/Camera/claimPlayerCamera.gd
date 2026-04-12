extends Node
class_name ClaimPlayerCamera

@onready var parent:Camera2D = $".."
@export var player:Node2D

func _ready() -> void:
	if int(player.name) == multiplayer.get_unique_id():
		pass
		parent.make_current()
	else:
		parent.enabled = false
