extends Node

# WITH THIS METHOD
# YOU NEED TO COPY THE PYTHON FILE NEXT TO THE EXPERTED EXECUTABLE

var DIR = OS.get_executable_path().get_base_dir()
var interpreter_path = DIR.path_join("Python/Venv/Scripts/python.exe")
var script_path = DIR.path_join("Python/test_script.py")




func _ready() -> void:
	if !OS.has_feature("standalone"):
		interpreter_path = ProjectSettings.globalize_path("res://Python/Venv/Scripts/python.exe")
		script_path = ProjectSettings.globalize_path("res://Python/test_script.py")
	print(interpreter_path)
	print(script_path)
	OS.execute(interpreter_path, [script_path])
