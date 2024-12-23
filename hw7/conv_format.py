import sys

class Converter:
    def __init__(self, file: list[str]) -> str:
        total_output = ""
        for line in file:
            if line != "":
                total_output += self.convert_line(line) + "\n"
        print(total_output)

    def convert_line(self, line: str) -> str:
        tokenized_line = line.strip().split()
        midpoint = tokenized_line.index("=>")
        output = ""
        for i in range(midpoint):
            word = tokenized_line[i]
            state = tokenized_line[i + midpoint + 2].split("_")[1]
            output += f"{word}/{state} "
        return output

def main():
    data = sys.stdin.read().splitlines()
    Converter(data)

if __name__ == "__main__":
    main()