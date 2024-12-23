import sys

frequencies = {}
for line in sys.stdin:
    tokens = line.split()

    for token in tokens:
        if token in frequencies:
            frequencies[token] += 1
        else:
            frequencies[token] = 1

for word in frequencies:
    print(word + "	" + str(frequencies[word]))