import argparse
import numpy as np
#there's a new kid in town, check_hmm is so last week
from generate_hmm import HMMGenerator

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--hmm', type=str, required=True, help='HMM model file')
arg_parser.add_argument('--input', type=str, required=True, help='File with test sequences')
args = arg_parser.parse_args()

class Viterbi:
    def __init__(self, 
                 test_file: str, 
                 state_indices: dict, 
                 sym_indices: dict, 
                 init_states: np.ndarray, 
                 trans_states: np.ndarray, 
                 emiss_states: np.ndarray) -> None:
        self.observations = self.observe(test_file)
        self.state_indices = state_indices
        self.sym_indices = sym_indices
        self.init_states = init_states
        self.trans_states = trans_states
        self.emiss_states = emiss_states
        self.index_to_state = {self.state_indices[state]: state for state in self.state_indices}

    def observe(self, file_path: str):
        with open(file_path, 'r') as file:
            return [(line).strip().split() for line in file.readlines()]
    
    def generate_output(self) -> str:
        output = ""
        for observation in self.observations:
            output += self.viterbize_line(observation) + "\n"
        return output

    def viterbize_line(self, observation: list[str]) -> str:
        state_count = len(self.state_indices)
        obs_count = len(observation) + 1
        trellis = np.zeros((state_count, obs_count), dtype=np.float64) #trellis is the type of table that the viterbi algorithm uses! The more you know <3
        backpointers = np.zeros((state_count, obs_count), dtype=int)
        trellis[:, 0] = self.init_states[:, 0]
        path = [0] * obs_count
        path[0] = trellis[:, 0].argmax()

        for t in range(1, obs_count):
            sym = observation[t-1].lower()
            if sym not in self.sym_indices:
                sym = "<unk>"
            sym_index = self.sym_indices[sym]
            for s in range(state_count):
                tr_probs = trellis[:, t-1] + self.trans_states[:, s] #this gives us the slice of the entire previous column of tr_probs
                emiss_prob = self.emiss_states[s, sym_index] #this is constant, so we just need the one emiss_prob
                trellis[s, t] = tr_probs.max() + emiss_prob #instead of looping through everything, we can just add the max tr_prob with the emission prob
                backpointers[s, t] = tr_probs.argmax() #backpointers for each state and transition indicate the index of transition state with the highest prob
        best_last_state = trellis[:, obs_count - 1].argmax()
        path[obs_count - 1] = best_last_state
        for i in range(obs_count - 2, -1, -1):
            path[i] = backpointers[path[i+1], i+1]
        state_path = [self.index_to_state[i] for i in path]
        return f"{' '.join(observation)} => {' '.join(state_path)} {str(trellis[best_last_state, obs_count-1])}"

def main():
    with open(args.hmm, 'r') as hmm_file:
        hmm_generator = HMMGenerator(hmm_file)
        state_indices = hmm_generator.state_indices
        sym_indices = hmm_generator.sym_indices
        hmm_init_states = hmm_generator.init_states
        hmm_trans_states = hmm_generator.trans_states
        hmm_emiss_states = hmm_generator.emiss_states
        viterbi = Viterbi(args.input, 
                          state_indices,
                          sym_indices,
                          hmm_init_states,
                          hmm_trans_states,
                          hmm_emiss_states)
        print(viterbi.generate_output())
    
if __name__ == "__main__":
    main()
