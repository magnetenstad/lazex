from analyse import lines_analyse

def file_read(path):
	with open(path, "r") as file:
		return file.readlines()

def file_write(path, lines):
	with open(path, "w") as file:
		file.writelines(lines)

def file_compile(path):
	lines = file_read(path)

	lines = lines_analyse(lines)

	file_write(path.partition(".")[0] + ".tex", lines)

file_compile("test.txt")
