import math
from collections import defaultdict
import numpy as np

class HMMChecker:
    def __init__(self, hmm: str) -> None:
        self.hmm = {}
        self.init_states = {}
        self.trans_states = defaultdict(lambda: defaultdict(tuple))
        self.emiss_states = defaultdict(lambda: defaultdict(tuple))
        self.sym_set = set()
        self.state_set = set()
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
            elif line.startswith("\\init"):
                i = self.process_init(hmm[i:], i)
            elif line.startswith("\\transition"):
                i = self.process_transition(hmm[i:], i)
            elif line.startswith("\\emission"):
                i = self.process_emission(hmm[i:], i)
            i += 1
        if self.state_num != len(self.state_set):
            self.warnings["state_num"] = f"warning: different numbers of state_num: claimed={self.state_num}, real={len(self.emiss_states)}"
        else: 
            self.warnings["state_num"] = f"state_num={self.state_num}"
        if self.sym_num != len(self.sym_set):
            self.warnings["sym_num"] = f"warning: different numbers of sym_num: claimed={self.sym_num}, real={len(self.sym_set)}"
        else:
            self.warnings["sym_num"] = f"sym_num={self.sym_num}"

    
    def print_warnings(self) -> None:
        warnings = f"""{self.warnings["state_num"]}
{self.warnings["sym_num"]}
{self.warnings["init_line_num"]}
{self.warnings["trans_line_num"]}
{self.warnings["emiss_line_num"]}
{self.warnings["init_warnings"]}{self.warnings["trans_warnings"]}{self.warnings["emiss_warnings"]}
        """

    def process_init(self, init_section: list[str], line_num: int) -> int:
        finished = False
        i = 1
        curr_state = ""
        while not finished:
            line = init_section[i].strip().split()
            if line == []:
                finished = True
            else:
                state = line[0]
                self.state_set.add(state)
                prob = float(line[1])
                self.init_states[state] = prob
                i += 1
                if curr_state != state:
                    if curr_state != '':
                        prob_sum = 0
                        for prob in self.init_states[curr_state]:
                            prob_sum += prob
                        if round(prob_sum, 3) != 1.0:
                            self.warnings["init_warnings"] += f"warning: the init_prob_sum for state {curr_state} is {prob_sum}\n"
                    curr_state = state
        warning_header = ""
        if i - 1 != self.init_line_num:
            warning_header += f"warning: different numbers of init_line_num: claimed={self.init_line_num}, real={i - 1}"
        else:
            warning_header += f"init_line_num = {self.init_line_num}"
        self.warnings["init_line_num"] = warning_header + self.warnings["init_line_num"]
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
                self.state_set.add(init_state)
                self.state_set.add(trans_state)
                prob = float(line[2])
                if len(line) > 3 and not line[3].startswith("#"):
                    log_prob = float(line[3])
                    self.trans_states[init_state][trans_state] = (prob, log_prob)
                else:
                    self.trans_states[init_state][trans_state] = (prob, math.log10(prob))
                i += 1
        for state in self.trans_states:
            trans_prob_sum = 0
            for transition in self.trans_states[state]:
                trans_prob_sum += self.trans_states[state][transition][0]
            if round(trans_prob_sum, 3) != 1.0:
                self.warnings["trans_warnings"] += f"warning: the trans_prob_sum for state {state} is {trans_prob_sum}\n"
        warning_header = ""
        if i - 1 != self.trans_line_num:
            warning_header = f"warning: different numbers of trans_line_num: claimed={self.trans_line_num}, real={i - 1}"
        else: 
            warning_header = f"trans_line_num = {i}"
        self.warnings["trans_line_num"] = warning_header
        return line_num + i
    
    def process_emission(self, emiss_section: list[str], line_num: int) -> int:
        i = 1
        while i < len(emiss_section):
            line = emiss_section[i].strip().split()
            if not line:
                break
            state = line[0]
            symbol = line[1]
            self.sym_set.add(symbol)
            self.state_set.add(state)
            prob = float(line[2])
            if len(line) > 3 and not line[3].startswith("#"):
                log_prob = float(line[3])
                self.emiss_states[state][symbol] = (prob, log_prob)
            else:
                self.emiss_states[state][symbol] = (prob, math.log10(prob)) if prob != 0.0 else (prob, -np.inf)
            i += 1
        for state in self.state_set:
            emiss_prob_sum = 0
            for emission in self.emiss_states[state]:
                emiss_prob_sum += self.emiss_states[state][emission][0]
            if round(emiss_prob_sum, 3) != 1.0:
                self.warnings["emiss_warnings"] += f"warning: the emiss_prob_sum for state {state} is {emiss_prob_sum}\n"
        warning_header = ""
        if i - 1 != self.emiss_line_num:
            warning_header = f"warning: different numbers of emiss_line_num: claimed={self.emiss_line_num}, real={i - 1}"
        else: 
            warning_header = f"emiss_line_num = {i}\n"
        self.warnings["emiss_line_num"] = warning_header
        return line_num + i