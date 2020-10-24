functions = {}
mode_math = False

def analyse_division(string):
	parts = string.partition("/")
	dividend, divisor = parts[0], parts[2]
	start, end = "", ""
	for i0 in range(len(parts[0])-1, -1, -1):
		char = parts[0][i0]
		if char in "]":
			depth = 0
			b = False
			for i in range(i0, -1, -1):
				c = parts[0][i]
				depth += (c in "[") - (c in "]")
				if depth == 0 and c in "[":
					start = parts[0][:i]
					dividend = parts[0][i:]
					b = True
					break
			if b:
				break
		elif char in "=+-":
			start = parts[0][:i0+1]
			dividend = parts[0][i0+1:]
			break
	for i1 in range(len(parts[2])):
		char = parts[2][i1]
		if char in "[":
			depth = 0
			b = False
			for i in range(i1, len(parts[2])):
				c = parts[2][i]
				depth += (c in "[") - (c in "]")
				if depth == 0 and c in "]":
					end = parts[2][i:]
					divisor = parts[2][:i]
					b = True
					break
			if b:
				break
		elif char in "=+-":
			end = parts[2][i1-1:]
			divisor = parts[2][:i1-1]
			break
	return (start + "\\frac{" + dividend + "}{" + divisor + "}" + end).replace(" ", "")

def analyse_string(string):
	if "/" in string:
		string = analyse_division(string)
	return "[" + string + "]"

def analyse_line(line):
	global mode_math
	tabs = line.count("\t")
	line = line.rstrip("\n").replace("\t", "")

	if mode_math:
		string = "(" + line + ")"
		i = 0
		prev = 0
		while i < len(string):
			char = string[i]
			if char == ")":
				string = string[:prev] + analyse_string(string[prev+1:i]) + string[i+1:]
				i = 0
				prev = 0
			elif char == "(":
				prev = i
			i += 1
		if string[0] == "[" and string[-1] == "]":
			string = string[1:-1]
		
		line = string
	command = []

	if line[0] == "\\" and not line[1] == "\\" and not "{" in line:
		space = line.find(" ")
		line = line[:space] + "{" + line[space+1:] + "}"
	if line.startswith("\\begin"):
		command = ["add", tabs, "\t" * tabs + line.replace("\\begin", "\\end")]
		if "align" in line or "equation" in line:
			mode_math = True
	if line.startswith("\\end"):
		if "align" in line or "equation" in line:
			mode_math = False
	if line.startswith( "\\def"):
		start = line.find(" ")+1
		end = line.find("}")+1
		functions[line[start:end]] = line[end:].strip()
		print(functions)
		return "", ["pop"]
	else:
		for f in functions:
			search = "$" + f.split("{")[0]
			args = f[f.find("{")+1:f.find("}")].replace(" ", "").split(",")
			while search in line:
				start = line.find(search)
				end = start + line[start:].find("}")
				arguments = line[start+len(search)+1:end].replace(" ", "").split(",")
				output = functions[f]
				print(args)
				print(arguments)
				for i in range(len(args)):
					output = output.replace(args[i], arguments[i])
				line = line[:start] + output + line[end+1:]
	
	if mode_math:
		line = line.replace("[", "\\left(")
		line = line.replace("]", "\\right)")
		line = line.replace("sqrt", "\\sqrt")

		if line[0] != "\\":
			line = line.replace("*", "\\cdot")
			line += "\\\\"
		
	return "\t" * tabs + line + "\n", command

def analyse_lines(lines):
	i = 0
	while i < len(lines):
		if lines[i].isspace():
			lines.pop(i)
			continue
		lines[i], command = analyse_line(lines[i])
		if len(command):
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
		i += 1
	return lines
