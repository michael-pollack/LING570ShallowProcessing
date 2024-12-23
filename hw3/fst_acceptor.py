import re
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--fst', type=str, required=True, help='input grammar')
arg_parser.add_argument('--input', type=str, required=True, help='input destination')
args = arg_parser.parse_args()

class FSAChecker:
    def __init__(self, fst_file: str):
        self.start_state, self.terminus, self.input_map = self.make_input_map(fst_file)

    def tokenize(self, edge: str) -> tuple[str, str, str, str, float]:
        token_pattern = r'\"[^\"]*\"|\*e\*|\d+\.\d+|\d+|\w+'
        tokens = re.findall(token_pattern, edge)
        start = tokens[0] if tokens else None
        finish = tokens[1] if len(tokens) > 1 else None
        input = tokens[2] if len(tokens) > 2 else None
        output = tokens[3] if len(tokens) > 3 else None
        weight = float(tokens[4]) if len(tokens) > 4 else None
        return start, finish, input, output, weight

    def make_fst_relations(self, line: str, input_map: dict) -> dict:
        start, finish, input, output, weight = self.tokenize(line)
        if start in input_map:
            input_map[start].append((finish, input, output, weight))
        else:
            input_map[start] = [(finish, input, output, weight)]
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
                        start, _, _, _, _ = self.tokenize(line)
                    input_map = self.make_fst_relations(line, input_map)
        if terminus and terminus not in input_map:
            input_map[terminus] = []
        return start, terminus, input_map
    
    def input_checker(self, curr, output, weight, states: list[str]) -> tuple[str, int]:
        #Base cases
        if not states:
            #Base case for terminus with no necessary input
            for edge in self.input_map[curr]:
                if edge[0] == self.terminus and edge[1] == '*e*':
                    new_output = output + " " + edge[2]
                    new_weight = weight * edge[3] if edge[3] is not None else weight
                    return new_output, new_weight
            #Normal base case
            if curr == self.terminus:
                return output, weight
            else:
                return '*none*', 0
        else:
            if curr not in self.input_map:
                return '*none*', 0
            edges = self.input_map[curr]
            best_output, best_weight = '*none*', 0

            for edge in edges:
                if edge[1] == states[0]:
                    new_output = output + " " + edge[2]
                    new_weight = weight * edge[3] if edge[3] is not None else weight
                    result_output, result_weight = self.input_checker(edge[0], new_output, new_weight, states[1:])
                    if result_weight > best_weight:
                        best_output, best_weight = result_output, result_weight
                elif edge[1] == '*e*':
                    new_output = output + " " + edge[2]
                    new_weight = weight * edge[3] if edge[3] is not None else weight
                    result_output, result_weight = self.input_checker(edge[0], output, weight, states)
                    if result_weight > best_weight:
                        best_output, best_weight = result_output, result_weight
        return best_output, best_weight
    
    def process_expressions(self, input_file: str) -> None:
        with open(input_file, 'r') as input_text:
            for line in input_text:
                states = line.split()
                output, weight = self.input_checker(self.start_state, '', 1, states)
                print(line.strip() + " => " + output + " " + str(weight))

def main():
    checker = FSAChecker(args.fst)
    checker.process_expressions(args.input)

if __name__ == "__main__":
    result = main()