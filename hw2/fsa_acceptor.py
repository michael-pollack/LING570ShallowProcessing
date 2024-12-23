import re
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--fsa', type=str, required=True, help='input grammar')
arg_parser.add_argument('--input', type=str, required=True, help='input destination')
args = arg_parser.parse_args()

class FSAChecker:
    def __init__(self, fsa_file: str):
        self.start_state, self.terminus, self.input_map = self.make_input_map(fsa_file)

    def tokenize(self, edge: str) -> tuple[str, str, str]:
        token_pattern = r'\"[^\"]*\"|\w+|\*e\*'
        tokens = re.findall(token_pattern, edge)
        start = tokens[0] if tokens else None
        finish = tokens[1] if len(tokens) > 1 else None
        input = tokens[2] if len(tokens) > 2 else None
        return  start, finish, input

    def make_fsa_relations(self, line: str, input_map: dict) -> dict:
        start, finish, input = self.tokenize(line)
        if start in input_map:
            input_map[start].append((finish, input))
        else:
            input_map[start] = [(finish, input)]
        return input_map

    def make_input_map(self, file: str) -> tuple[str, str, dict]:
        start, terminus = None, None
        input_map = {}
        with open(file, 'r') as regex:
            for line in regex:
                if terminus is None:
                    terminus = line.strip()
                else:
                    if start is None: 
                        start, _, _ = self.tokenize(line)
                    input_map = self.make_fsa_relations(line, input_map)
        return start, terminus, input_map
        
    def input_checker(self, curr, states: list[str]) -> bool:
        if not states:
            for edge in self.input_map[curr]:
                if edge[0] == self.terminus and edge[1] == '*e*':
                    return True
            return curr == self.terminus
        else:
            if curr not in self.input_map:
                return False
            edges = self.input_map[curr]
            for edge in edges:
                if edge[1] == states[0]:
                    if self.input_checker(edge[0], states[1:]):
                        return True
                elif edge[1] == '*e*':
                    if self.input_checker(edge[0], states):
                        return True
        return False
    
    def process_expressions(self, input_file: str):
        with open(input_file, 'r') as input_text:
            for line in input_text:
                states = line.split()
                passes = "yes" if self.input_checker(self.start_state, states) else "no"
                print(line.strip() + " => " + passes)

def main():
    checker = FSAChecker(args.fsa)
    checker.process_expressions(args.input)

if __name__ == "__main__":
    result = main()