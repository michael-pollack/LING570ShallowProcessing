import math
from collections import defaultdict
import numpy as np

class HMMGenerator:
    def __init__(self, hmm: str) -> None:
        self.hmm = {}
        self.state_indices = {}
        self.sym_indices = {}
        self.state_index = 0
        self.sym_index = 0
        self.state_num = -1
        self.sym_num = -1
        self.init_line_num = -1
        self.trans_line_num = -1
        self.emiss_line_num = -1
        self.warnings = {
            "state_num": "",
            "sym_num": "",
            "init_line_num": "",
            "trans_line_num": "",
            "emiss_line_num": "",
            "init_warnings": "",
            "trans_warnings": "",
            "emiss_warnings": ""
        }
        self.processHMM(hmm)

    def processHMM(self, hmmfile) -> None:
        i = 0
        hmm = hmmfile.readlines()
        while i < len(hmm):
            line = hmm[i]
            if line.startswith("state_num"):
                self.state_num = int(line.strip().split("=")[1])
            elif line.startswith("sym_num"):
                self.sym_num = int(line.strip().split("=")[1])
            elif line.startswith("init_line_num"):
                self.init_line_num = int(line.strip().split("=")[1])
            elif line.startswith("trans_line_num"):
                self.trans_line_num = int(line.strip().split("=")[1])
            elif line.startswith("emiss_line_num"):
                self.emiss_line_num = int(line.strip().split("=")[1])
                #finished header, create tables
                self.process_header()
            elif line.startswith("\\init"):
                i = self.process_init(hmm[i:], i)
            elif line.startswith("\\transition"):
                i = self.process_transition(hmm[i:], i)
            elif line.startswith("\\emission"):
                i = self.process_emission(hmm[i:], i)
            i += 1

    def process_header(self) -> None:
        self.init_states = np.full((self.state_num, 1), -np.inf)
        self.trans_states = np.full((self.state_num, self.state_num), -np.inf)
        self.emiss_states = np.full((self.state_num, self.sym_num), -np.inf)

    def process_init(self, init_section: list[str], line_num: int) -> int:
        finished = False
        i = 1
        while not finished:
            line = init_section[i].strip().split()
            if line == []:
                finished = True
            else:
                state = line[0]
                if state not in self.state_indices:
                    self.state_indices[state] = self.state_index
                    self.state_index += 1
                state_index = self.state_indices[state]
                prob = float(line[1])
                if len(line) > 2 and not line[2].startswith("#"):
                    log_prob = float(line[2])
                else:
                    log_prob = -np.inf if prob == 0.0 else math.log10(prob)
                self.init_states[state_index, 0] = log_prob
                i += 1
        return line_num + i
    
    def process_transition(self, trans_section: list[str], line_num: int) -> int:
        finished = False
        i = 1
        while not finished:
            line = trans_section[i].strip().split()
            if line == []:
                finished = True
            else:
                init_state = line[0]
                trans_state = line[1]
                if init_state not in self.state_indices:
                    self.state_indices[init_state] = self.state_index
                    self.state_index += 1
                if trans_state not in self.state_indices:
                    self.state_indices[trans_state] = self.state_index
                    self.state_index += 1
                init_index = self.state_indices[init_state]
                trans_index = self.state_indices[trans_state]
                prob = float(line[2])
                if len(line) > 3 and not line[3].startswith("#"):
                    log_prob = float(line[3])
                else:
                    log_prob = -np.inf if prob == 0.0 else math.log10(prob)
                self.trans_states[init_index, trans_index] = log_prob
                i += 1
        return line_num + i
    
    def process_emission(self, emiss_section: list[str], line_num: int) -> int:
        i = 1
        while i < len(emiss_section):
            line = emiss_section[i].strip().split()
            if not line:
                break
            state = line[0]
            symbol = line[1]
            prob = float(line[2])
            std_sym = symbol.lower()
            if state not in self.state_indices:
                self.state_indices[state] = self.state_index
                self.state_index += 1
            if std_sym not in self.sym_indices:
                self.sym_indices[std_sym] = self.sym_index
                self.sym_index += 1
            state_index = self.state_indices[state]
            sym_index = self.sym_indices[std_sym]
            if len(line) > 3 and not line[3].startswith("#"):
                log_prob = float(line[3])
            else:
                log_prob = -np.inf if prob == 0.0 else math.log10(prob)
            self.emiss_states[state_index, sym_index] = log_prob
            i += 1
        return line_num + i
    