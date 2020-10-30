from lib import compile_lines

def file_read(path):
	with open(path, "r") as file:
		return file.readlines()

def file_write(path, lines):
	with open(path, "w") as file:
		file.writelines(lines)

def lazex_to_latex(path):
	lines = file_read(path)
	lines = compile_lines(lines)
	file_write(path.partition(".")[0] + ".tex", lines)

lazex_to_latex("test.txt")
