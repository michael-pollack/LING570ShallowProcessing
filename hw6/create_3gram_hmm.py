import re
import sys
import math
from collections import defaultdict
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--unkprobs', type=str, required=True, help='input destination')
arg_parser.add_argument('--l1', type=str, required=True, help='input destination')
arg_parser.add_argument('--l2', type=str, required=True, help='input destination')
arg_parser.add_argument('--l3', type=str, required=True, help='input destination')
args = arg_parser.parse_args()

class HMMGenerator:
    def __init__(self, data: str, unkprobs: str, l1: float, l2: float, l3: float):
        self.data = self.tokenize(data)
        self.unkprobs = self.process_unkprobs(unkprobs)
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.state_set = set()
        self.sym_set = set()
        print(self.construct_hmm())

    def construct_hmm(self) -> str:
        transitions, trans_line_num = self.transition_probs(self.data)
        emissions, emiss_line_num = self.emission_probs(self.data)
        init, init_line_num = self.init_state(self.data)
        hmm = f"""state_num={len(self.state_set) + 1}
sym_num={len(self.sym_set)}
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
    
    def process_unkprobs(self, unkprobs: str) -> dict:
        unkprobs_map = {}
        for line in unkprobs:
            tokenized_line = re.findall(r"\S+", line)
            unkprobs_map[tokenized_line[0]] = float(tokenized_line[1])
        return unkprobs_map

    def transition_probs(self, data: list[tuple[str, str]]) -> tuple[str, int]:
        mono_counts = defaultdict(float)
        bi_counts = defaultdict(lambda: defaultdict(float))
        tri_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        smoothed_probs = defaultdict(lambda: defaultdict(float))
        lines = 0
        printed_transitions = ""

        for i in range(len(data) - 1):
            start = data[i][1]
            mono_counts[start] += 1
            if i < len(data) - 2:
                middle = data[i + 1][1]
                bi_counts[start][middle] += 1
                if i < len(data) - 3:
                    end = data[i + 2][1]
                    tri_counts[start][middle][end] += 1

        #turn mono_counts into mono_probs
        mono_dist_size = sum(mono_counts[value] for value in mono_counts)
        mono_probs = {item: float(mono_counts[item] / mono_dist_size) for item in mono_counts}

        #turn bi_counts into bi_probs
        bi_probs = defaultdict(lambda: defaultdict(int))
        for start in bi_counts:
            prob_dist = bi_counts[start]
            prob_dist_size = sum([prob_dist[value] for value in prob_dist])
            for end in prob_dist:
                prob = float(prob_dist[end] / prob_dist_size)
                bi_probs[start][end] = prob

        #turn tri_counts into tri_probs
        tri_probs = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for start in tri_counts:
            for middle in tri_counts[start]:
                prob_dist = tri_counts[start][middle]
                prob_dist_size = sum([prob_dist[value] for value in prob_dist])
                for end in prob_dist:
                    prob = float(prob_dist[end] / prob_dist_size)
                    tri_probs[start][middle][end] = prob

        #smooth it out babeyyyy
        for start in mono_probs:
            for middle in mono_probs:
                for end in mono_probs:
                    init_state = start + "_" + middle
                    trans_state = middle + "_" + end
                    self.state_set.add(init_state)
                    self.state_set.add(trans_state)
                    p1 = mono_probs[end]
                    p2 = bi_probs[middle][end] if bi_probs[middle][end] else 0
                    if bi_probs == 0:
                        p3 = 0 if end == 'BOS' else float(1 / mono_dist_size + 1)
                    else:
                        p3 = tri_probs[start][middle][end]
                    smoothed_prob = (self.l3 * p3) + (self.l2 * p2) + (self.l1 * p1)
                    smoothed_probs[init_state][trans_state] = smoothed_prob

        #Now lets make! that! list!
        smoothed_probs = dict(sorted(smoothed_probs.items()))
        for init_state in smoothed_probs:
            trans_probs = dict(sorted(smoothed_probs[init_state].items()))
            for trans_state in trans_probs:
                printed_transitions += f"{init_state}\t{trans_state}\t{smoothed_probs[init_state][trans_state]}\n"
                lines += 1

        return printed_transitions, lines

    def emission_probs(self, data: list[tuple[str, str]]) -> tuple[str, int, int, int]:
        symbol_set = set()
        probs = defaultdict(lambda: defaultdict(float))
        lines = 0
        for i in range(len(data)):
            if i < (len(data) - 1):
                symbol = data[i + 1][0]
                init_state = data[i][1]
                trans_state = data[i + 1][1]
                transition = init_state + "_" + trans_state
                probs[transition][symbol] += 1
            else: 
                symbol = data[i][0]
                init_state = data[i][1]
            self.sym_set.add(symbol)
            self.state_set.add(transition)
        probs = dict(sorted(probs.items()))
        printed_emissions = ""
        for transition  in probs:
            prob_dist = dict(sorted(probs[transition].items()))
            prob_dist_size = sum([prob_dist[value] for value in prob_dist])
            for symbol in prob_dist:
                trans_state = transition.split("_")[1]
                if trans_state in self.unkprobs:
                    unkprob = self.unkprobs[trans_state]
                else: 
                    unkprob = 0
                prob = (prob_dist[symbol] / prob_dist_size) * (1 - unkprob)
                printed_emissions += f"{transition}\t{symbol}\t{prob}\n" 
                lines += 1
        return printed_emissions, lines
    
data = sys.stdin.read().splitlines()
def main():
    with open(args.unkprobs, 'r') as unkprobs:
        HMMGenerator(data, unkprobs, float(args.l1), float(args.l2), float(args.l3))

if __name__ == "__main__":
    result = main()