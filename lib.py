TEXT = 0
MATH = 1
MODE = TEXT
DEBUG = False


class Function:
    def __init__(self, name, arguments, content) -> None:
        self.name = name
        self.arguments = arguments
        self.content = content


functions = [Function("$eval", "", "")]


def string_insert(string, index, substring):
    return string[:index] + substring + string[index:]


def string_replace_all(string, lst):
    for old, new in lst:
        string = string.replace(old, new)
    return string


def depth_add(char):
    return (char in ("(", "{", "[")) - (char in (")", "}", "]"))


def pad_symbols(string):
    symbols = ("!", "=", "+", "-", "*", "/", ">", "<")
    i, depth = 0, 0
    while i < len(string):
        depth += depth_add(string[i])
        if (depth == 0) and (string[i] in symbols):
            if (string[i] != "=") or (string[i - 1] in symbols):
                string = string_insert(string, i, " ")
                i += 1
            if string[i + 1] != "=":
                string = string_insert(string, i + 1, " ")
        i += 1
    return string


def compute(string):
    replace = (("[", "("), ("]", ")"), ("{", "("), ("}", ")"), ("^", "**"))
    string = compile_brackets(string, latex=False)
    string = string_replace_all(string, replace)
    return str(eval(string))


def compile_expression(string, latex=True):

    # Insert functions
    for func in functions:
        while func.name in string:
            start = string.find(func.name)
            depth, end = 0, 0
            for i in range(len(string[start:])):
                depth += depth_add(string[start:][i])
                if depth == 0 and string[start:][i] == "}":
                    end = start + i
                    break

            if func.name == "$eval":
                output = compute(string[start + len(func.name) + 1 : end])
            else:
                arguments = (
                    string[start + len(func.name) + 1 : end].replace(" ", "").split(",")
                )
                content = func.content
                for i in range(min(len(func.arguments), len(arguments))):
                    content = content.replace(
                        func.arguments[i], "(" + arguments[i] + ")"
                    )
                output = compile_brackets(content, latex=latex)

            string = string[:start] + output + string[end + 1 :]

    # Handle math
    if latex and MODE == MATH:
        words = pad_symbols(string).split(" ")

        while "" in words:
            words.remove("")

        while "/" in words:
            i = words.index("/")
            dividend, divisor = words.pop(i - 1), words.pop(i)
            words[i - 1] = "\\frac{" + dividend + "}{" + divisor + "}"

        return "[" + "".join(words) + "]"
    else:
        return "[" + string + "]"


def compile_brackets(line, latex=False):
    global MODE

    if MODE == MATH:
        string = "(" + line + ")"
        i, prev = 0, 0

        while i < len(string):
            if string[i] == ")":
                string = (
                    string[:prev]
                    + compile_expression(string[prev + 1 : i], latex=latex)
                    + string[i + 1 :]
                )
                i, prev = 0, 0
            elif string[i] == "(":
                prev = i
            i += 1

        if string[0] == "[" and string[-1] == "]":
            string = string[1:-1]
        line = string

    return line


def compile_line(line, latex=True):
    global MODE

    tabs = line.count("\t")
    line = line.rstrip("\n").replace("\t", "")

    line = compile_brackets(line, latex=latex)

    if not latex:
        return line, []
    else:
        commands = []

        if line[0] == "\\" and not line[1] == "\\" and not "{" in line:
            space = line.find(" ")
            line = line[:space] + "{" + line[space + 1 :] + "}"

        if line.startswith("\\begin"):
            commands.append(
                ["add", tabs, "\t" * tabs + line.replace("\\begin", "\\end")]
            )
            if "align" in line or "equation" in line:
                commands.append(["math"])

        if line.startswith("\\end"):
            if "align" in line or "equation" in line:
                MODE = TEXT

        if line.startswith("\\def"):
            name = line[line.find(" ") + 1 : line.find("{")].replace(" ", "")
            arguments = (
                line[line.find("{") + 1 : line.find("}")].replace(" ", "").split(",")
            )
            content = line[line.find("}") + 1 :].replace(" ", "")
            functions.append(Function(name, arguments, content))
            commands.append(["pop"])
            return "", commands

        if MODE == MATH:
            line = line.replace("[", "\\left(")
            line = line.replace("]", "\\right)")
            line = line.replace("sqrt", "\\sqrt")

            if line[0] != "\\":
                line = line.replace("*", "\\cdot ")
                line += "\\\\"

        return "\t" * tabs + line + "\n", commands


def compile_lines(lines):
    global MODE
    i = 0
    while i < len(lines):

        # Remove empty line
        if lines[i].isspace():
            lines.pop(i)
            continue

        # Analyse line
        lines[i], commands = compile_line(lines[i])

        # Execute command
        for command in commands:
            if command[0] == "add":
                for j in range(i + 1, len(lines)):
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
