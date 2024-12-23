import argparse
import numpy as np
import re
from check_hmm import HMMChecker

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--hmm', type=str, required=True, help='HMM model file')
arg_parser.add_argument('--input', type=str, required=True, help='File with test sequences')
args = arg_parser.parse_args()

class ViterbiAlgo:
    def __init__(self, test_file: str, states: list[str], start_prob: dict, trans_prob: dict, emiss_prob: dict):
        self.observations = self.observe(test_file)
        self.states = states
        self.start_prob = start_prob
        self.trans_prob = trans_prob
        self.emiss_prob = emiss_prob

    def observe(self, file_path: str):
        with open(file_path, 'r') as file:
            return [("<s> " + line).strip().split() for line in file.readlines()]
    
    def generate_output(self) -> str:
        output = ""
        for observation in self.observations:
            output += self.viterbize_line(observation) + "\n"
        return output

    def viterbize_line(self, observation: list[str]) -> str:
        state_count = len(self.states)
        obs_count = len(observation)
        viterbi_table = np.zeros((state_count, obs_count), dtype=np.float64)
        backpointer = np.zeros((state_count, obs_count), dtype=int)

        #initializes table, sets everything to zero
        for s in range(state_count):
            state = self.states[s]
            prob = self.start_prob.get(state, 0.0) + self.emiss_prob[state].get(observation[0], (0.0, 0.0))[1]
            viterbi_table[s, 0] = prob
            backpointer[s, 0] = -1

        for t in range(obs_count - 1):
            for j in range(state_count):
                symbol = observation[t]
                state = self.states[j]
                max_prob = -np.inf
                max_back = -1
                for i in range(state_count):
                    prev_state = self.states[i]
                    prob = viterbi_table[i, t] + self.trans_prob[prev_state].get(state, (0.0, 0.0))[1] + self.emiss_prob[state].get(symbol, (0.0, 0.0))[1]
                    if prob > max_prob:
                        max_prob = prob
                        max_back = i
                viterbi_table[j, t+1] = max_prob
                backpointer[j, t+1] = max_back

        best_last_state = viterbi_table[:, obs_count - 1].argmax(axis=0)
        j = best_last_state
        path = [self.states[j]]
        for t in range(obs_count - 1, 0, -1):
            i = backpointer[j, t]
            path.append(self.states[i])
            j = i

        return f"{' '.join(observation[1:])} => {' '.join(path[::-1])} {str(viterbi_table[best_last_state, obs_count-1])}"

def main():
    with open(args.hmm, 'r') as hmm_file:
        checker = HMMChecker(hmm_file)
        hmm_states = list(checker.state_set)
        hmm_init_prob = checker.init_states
        hmm_trans_prob = checker.trans_states
        hmm_emiss_prob = checker.emiss_states
        viterbi = ViterbiAlgo(args.input, hmm_states, hmm_init_prob, hmm_trans_prob, hmm_emiss_prob)
        print(viterbi.generate_output())
    
if __name__ == "__main__":
    main()
