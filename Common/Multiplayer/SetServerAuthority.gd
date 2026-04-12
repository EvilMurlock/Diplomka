extends Node
class_name SetServerAuthority


func _enter_tree() -> void:
	if multiplayer.is_server():
		$"..".set_multiplayer_authority(1)
		
#func _ready() -> void:
#	if multiplayer.is_server():
#		$"..".set_multiplayer_authority(1)
