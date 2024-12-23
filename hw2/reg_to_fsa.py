import sys
first_line = True

output = ""
for line in sys.stdin:
    tokens = line.split()
    if len(tokens) == 3:
        output += "(" + tokens[0] + " (" + tokens[2] + " " + tokens[1] + "))\n"
    elif len(tokens) == 2:
        output = tokens[0] + "\n" + output

print(output)