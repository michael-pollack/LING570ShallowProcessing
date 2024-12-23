import re
import sys
import math
from collections import defaultdict
import argparse

arg_parser = argparse.ArgumentParser()
# arg_parser.add_argument('--input', type=str, required=True, help='input destination')
args = arg_parser.parse_args()

class HMMGenerator:
    def __init__(self, data):
        print(self.construct_hmm(data))

    def construct_hmm(self, data: str) -> str:
        tokenized_data = self.tokenize(data)
        transitions, trans_line_num = self.transition_probs(tokenized_data)
        emissions, state_num, sym_num, emiss_line_num = self.emission_probs(tokenized_data)
        init, init_line_num = self.init_state(tokenized_data)
        hmm = f"""state_num={state_num}
sym_num={sym_num}
init_line_num={init_line_num}
trans_line_num={trans_line_num}
emiss_line_num={emiss_line_num}

\\init
{init}

\\transition
{transitions}

\\emission
{emissions}
"""
        return hmm

    def tokenize(self, data: str) -> list[tuple[str, str]]:
        tokens = []
        for line in data:
            line = "<s>/BOS " + line + " <\\/s>/EOS"
            tokenized_line = re.findall(r"\S+", line)
            for token in tokenized_line:
                parts = re.split(r'(?<!\\)/', token)
                parts = [part.replace(r'\/', '/') for part in parts]
                tokens.append(tuple(parts))
        return tokens
    
    def init_state(self, data: list[tuple[str, str]]) -> tuple[str, int]:
        init_state = data[0][1]
        printed_init = f"{init_state}\t{1.0}\n"
        init_line_num = 1
        return printed_init, init_line_num

    def transition_probs(self, data: list[tuple[str, str]]) -> tuple[str, int]:
        probs = defaultdict(lambda: defaultdict(float))
        lines = 0
        for i in range(len(data)):
            if i < len(data) - 2:
                start = data[i][1]
                end = data[i + 1][1]
                probs[start][end] += 1
        probs = dict(sorted(probs.items()))
        printed_transitions = ""
        for start in probs:
            prob_dist = dict(sorted(probs[start].items()))
            prob_dist_size = sum([prob_dist[value] for value in prob_dist])
            for end in prob_dist:
                prob = prob_dist[end] / prob_dist_size
                printed_transitions += f"{start}\t{end}\t{prob}\n"
                lines += 1
        return printed_transitions, lines

    def emission_probs(self, data: list[tuple[str, str]]) -> tuple[str, int, int, int]:
        symbol_set = set()
        state_set = set()
        probs = defaultdict(lambda: defaultdict(float))
        lines = 0
        for i in range(len(data)):
            symbol = data[i][0]
            state = data[i][1]
            probs[state][symbol] += 1
            symbol_set.add(symbol)
            state_set.add(state)
        probs = dict(sorted(probs.items()))
        printed_emissions = ""
        for start  in probs:
            prob_dist = dict(sorted(probs[start].items()))
            prob_dist_size = sum([prob_dist[value] for value in prob_dist])
            for end in prob_dist:
                prob = prob_dist[end] / prob_dist_size
                printed_emissions += f"{start}\t{end}\t{prob}\n"
                lines += 1
        state_num, sym_num = len(state_set), len(symbol_set)
        return printed_emissions, state_num, sym_num, lines

data = sys.stdin.read().splitlines()
def main():
    HMMGenerator(data)

if __name__ == "__main__":
    result = main()