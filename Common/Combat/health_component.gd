extends Node
class_name HealthComponent

@export var maxHealth:float = 1

var health:float


func _ready() -> void:
	health = maxHealth
	
func applyDamage(damage:float) -> void:
	health -= damage
	print("Took %d damage, health = %d" % [damage, health])
	if health <= 0:
		get_parent().queue_free()
	
