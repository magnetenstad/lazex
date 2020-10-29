
TEXT = 0
MATH = 1
MODE = TEXT

functions = {
	"eval": ""
}

def space_string(string):
	symbols = ("!", "=", "+", "-", "*", "/", ">", "<")
	i = 0
	depth = 0
	while i < len(string):
		depth += (string[i] in ("(", "{", "[")) - (string[i] in (")", "}", "]"))
		if depth == 0 and string[i] in symbols:
			if string[i] != "=" or string[i-1] in symbols:
				string = string[:i] + " " + string[i:]
				i += 1
			if string[i+1] != "=":
				string = string[:i+1] + " " + string[i+1:]
		i += 1
	return string

def analyse_string(string, latex=True):
	for f in functions:
		search = "$" + f.split("{")[0]
		args = f[f.find("{")+1:f.find("}")].replace(" ", "").split(",")
		while search in string:
			start = string.find(search)
			depth = 0
			end = start
			for i in range(len(string[start:])):
				char = string[start:][i]
				depth += (char == "{") - (char == "}")
				if depth == 0 and char == "}":
					end = start + i
					break
			output = functions[f]
			if f == "eval":
				argument = string[start+len(search)+1:end]
				code = analyse_string(argument, latex=False)
				code = code.replace("[", "(").replace("]", ")")
				code = code.replace("{", "(").replace("}", ")")
				code = code.replace("^", "**")
				print(code)
				output = str(eval(code))
			else:
				arguments = string[start+len(search)+1:end].replace(" ", "").split(",")
				for i in range(min(len(args), len(arguments))):
					output = analyse_1(output.replace(args[i], arguments[i]), latex=latex)
			string = string[:start] + output + string[end+1:]

	if latex and MODE == MATH:
		words = space_string(string).split(" ")
		while "" in words:
			words.remove("")
		while "/" in words:
			i = words.index("/")
			dividend, divisor = words.pop(i-1), words.pop(i)
			words[i-1] = ("\\frac{" + dividend + "}{" + divisor + "}")
		return "[" + "".join(words) + "]"
	else:
		return "[" + string + "]"

def analyse_1(line, latex=False):
	global MODE
	if MODE == MATH:
		string = "(" + line + ")"
		i = 0
		prev = 0
		while i < len(string):
			char = string[i]
			if char == ")":
				string = string[:prev] + analyse_string(string[prev+1:i], latex=latex) + string[i+1:]
				i = 0
				prev = 0
			elif char == "(":
				prev = i
			i += 1
		if string[0] == "[" and string[-1] == "]":
			string = string[1:-1]
		
		line = string
	
	return line

def analyse_line(line, latex=True):
	global MODE
	tabs = line.count("\t")
	line = line.rstrip("\n").replace("\t", "")

	line = analyse_1(line, latex=latex)

	if latex:
		commands = []

		if line[0] == "\\" and not line[1] == "\\" and not "{" in line:
			space = line.find(" ")
			line = line[:space] + "{" + line[space+1:] + "}"
		if line.startswith("\\begin"):
			commands.append(["add", tabs, "\t" * tabs + line.replace("\\begin", "\\end")])
			if "align" in line or "equation" in line:
				commands.append(["math"])
		if line.startswith("\\end"):
			if "align" in line or "equation" in line:
				MODE = TEXT
		if line.startswith( "\\def"):
			start = line.find(" ")+1
			end = line.find("}")+1
			functions[line[start:end]] = line[end:].strip()
			commands.append(["pop"])
			return "", commands

		if MODE == MATH:
			line = space_string(line)

			line = line.replace("[", "\\left(")
			line = line.replace("]", "\\right)")
			line = line.replace("sqrt", "\\sqrt")

			if line[0] != "\\":
				line = line.replace("*", "\\cdot ")
				line += "\\\\"
			
	if latex:
		return "\t" * tabs + line + "\n", commands
	else:
		return line, []

def analyse_lines(lines):
	global MODE
	i = 0
	while i < len(lines):

		# Remove empty line
		if lines[i].isspace():
			lines.pop(i)
			continue
		
		# Analyse line
		lines[i], commands = analyse_line(lines[i])
		
		# Execute command
		for command in commands:
			if command[0] == "add":
				for j in range(i+1, len(lines)):
					if not lines[j].isspace() and lines[j].count("\t") <= command[1]:
						lines.insert(j, command[2])
						break
					elif j == len(lines) - 1:
						lines.insert(j + 1, command[2])
			elif command[0] == "pop":
				lines.pop(i)
				continue
			elif command[0] == "math":
				MODE = MATH
		
		# Go to next line
		i += 1

	return lines
