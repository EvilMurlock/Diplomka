extends Node
class_name BoolContainer

signal value_changed(value:bool)
var value:bool:
	set(v): 
		var changed:bool = value != v
		value = v
		if changed:
			value_changed.emit(value)
