extends Area2D
class_name HurtboxComponent

@export var healthComponent:HealthComponent

var hitboxes: Array[HitboxComponent] = []

func _on_area_entered(area: Area2D) -> void:
	if area is HitboxComponent:
		var hitbox = area as HitboxComponent
		
		if !hitboxes.has(hitbox):
			healthComponent.applyDamage(hitbox.damage)
			hitboxes.append(hitbox)


func _on_area_exited(area: Area2D) -> void:
	if area is HitboxComponent:
		var hitbox = area as HitboxComponent
		
		var index = hitboxes.find(hitbox)
		if index >= 0:
			hitboxes.remove_at(index)
