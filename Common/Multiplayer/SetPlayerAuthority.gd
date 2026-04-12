extends Node
class_name SetPlayerAuthority

@export var player:Node

func _enter_tree() -> void:
	#if multiplayer.is_server():
	$"..".set_multiplayer_authority(int(player.name))# MUST BE SET ON BOTH CLIENT AND SERVER, ELSE IT BUGS OUT, STILL GIVES AN ERROR DOU
		
#func _ready() -> void:
#	if multiplayer.is_server():
#		$"..".set_multiplayer_authority(int(player.name))
