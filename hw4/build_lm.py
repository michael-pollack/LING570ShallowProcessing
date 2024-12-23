from collections import defaultdict
import argparse
import math

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--input', type=str, required=True, help='input destination')
args = arg_parser.parse_args()

def main() -> None:
    with open(args.input, 'r') as file:
        lm_builder = LMBuilder(file, 3)
        lm_builder.print_lm()

class LMBuilder:
    def __init__(self, ngramFile: str, n: int) -> None:
        self.ngramcounts = defaultdict(int)
        self.n_minus_1_gram_counts = defaultdict(int)
        self.n = n
        self.load_ngram_counts(ngramFile)
        self.type_counts = []
        self.token_counts = []
        for i in range(1, self.n + 1):
            type_count = 0
            token_count = 0
            for ngram in self.ngramcounts:
                if len(ngram) == i:
                    type_count += 1
                    token_count += self.ngramcounts[ngram]
            self.type_counts.append(type_count)
            self.token_counts.append(token_count)

    def load_ngram_counts(self, ngramFile: str) -> None:
        for line in ngramFile:
            parts = line.strip().split()
            ngram = tuple(parts[1:])
            count = int(parts[0])
            self.ngramcounts[ngram] = count

    def get_ngram_probability(self, ngram: tuple) -> float:
        if len(ngram) == 1:
            return self.ngramcounts[ngram] / self.token_counts[0]
        else:
            n_minus_1_gram = ngram[:-1]
            ngram_count = self.ngramcounts.get(ngram, 0)
            n_minus_1_gram_count = self.ngramcounts.get(n_minus_1_gram, 0)
            if n_minus_1_gram_count > 0:
                return ngram_count / n_minus_1_gram_count
            else:
                return 0.0
            
    def get_log_prob(self, prob: float) -> float:
        return math.log10(prob) if prob > 0 else float('-inf')
    
    def print_lm(self) -> None:
        print("\\data\\")

        #Header
        for i in range(self.n):
            print(f"ngram {str(i + 1)}: type={str(self.type_counts[i])} token={str(self.token_counts[i])}")

        #Body
        for i in range(1, self.n + 1):
            print(f"\n\\{str(i)}-grams:")
            for ngram in self.ngramcounts: 
                if len(ngram) == i:
                    prob = self.get_ngram_probability(ngram)
                    log_prob = self.get_log_prob(prob)
                    if prob > 0:
                        print(f"{self.ngramcounts[ngram]} {prob} {log_prob} {' '.join(ngram)}")
        
        print("\\end\\")

if __name__ == "__main__":
    result = main()