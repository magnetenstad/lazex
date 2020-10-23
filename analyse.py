
def evaluate(string):
	if "/" in string:
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
		string = (start + "\\frac{" + dividend + "}{" + divisor + "}" + end).replace(" ", "")
	if "+" in string or "-" in string or "=" in string:
		string = "[" + string + "]"
	return string

def loop(string):
	string = "(" + string + ")"
	i = 0
	prev = 0
	while i < len(string):
		char = string[i]
		if char == ")":
			string = string[:prev] + evaluate(string[prev+1:i]) + string[i+1:]
			i = 0
			prev = 0
		elif char == "(":
			prev = i
		i += 1
	if string[0] == "[" and string[-1] == "]":
		string = string[1:-1]
	return string
	
def line_analyse(line):
	
	tabs = line.count("\t")
	line = line.rstrip("\n").replace("\t", "")

	line = loop(line)
	
	command = []

	if line[0] == "\\" and not line[1] == "\\" and not "{" in line:
		space = line.find(" ")
		line = line[:space] + "{" + line[space+1:] + "}"
	if "\\be" in line:
		command = [tabs, "\t" * tabs + line.replace("\\be", "\\en")]

	line = line.replace("\\ti", "\\title")
	line = line.replace("\\au", "\\author")
	line = line.replace("\\da", "\\date")
	line = line.replace("\\se", "\\section")
	line = line.replace("\\np", "\\newpage")
	line = line.replace("\\nl", "\\newline")
	line = line.replace("\\be", "\\begin")
	line = line.replace("\\en", "\\end")

	line = line.replace("[", "\\left(")
	line = line.replace("]", "\\right)")

	line = line.replace("@eq", "equation")
	line = line.replace("@al", "align")

	if line[0] != "\\":
		line = line.replace("*", "\\cdot")
		line += "\\\\"
	
	return "\t" * tabs + line + "\n", command

def lines_analyse(lines):	
	i = 0
	while i < len(lines):
		if lines[i].isspace():
			lines.pop(i)
			continue
		lines[i], command = line_analyse(lines[i])
		i += 1
		if len(command):
			for j in range(i, len(lines)):
				if not lines[j].isspace() and lines[j].count("\t") <= command[0]:
					lines.insert(j, command[1])
					break
				elif j == len(lines) - 1:
					lines.insert(j + 1, command[1])
	return lines
