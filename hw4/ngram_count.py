import re
from collections import defaultdict
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--input', type=str, required=True, help='input destination')
args = arg_parser.parse_args()

def main():
    counter = NGramCount()
    counter.print_ngrams(args.input, 3)

class NGramCount: 
    def __init__(self) -> None:
        pass

    def tokenize(self, line: str) -> list[str]:
        tokenized_line = re.findall(r"\S+", line)
        return tokenized_line
    
    def count(self, file: str, n: int) -> defaultdict:
        token_counter = defaultdict(int)
        for line in file:
            line = "<s> " + line + "</s>"
            start = 0
            end = n
            base_token_list = self.tokenize(line)
            ngram_token_list = []
            while end <= len(base_token_list):
                curr = []
                for i in range(start, end):
                    curr.append(base_token_list[i])
                ngram_token_list.append(' '.join(curr))
                start += 1
                end += 1
            for token in ngram_token_list:
                token_counter[token] += 1
        return token_counter

    def print_ngrams(self, input: str, n: int) -> None:
        i = 1
        while i <= n:
            with open(input, 'r') as file:
                token_counter = self.count(file, i)
                sorted_token_counter = {k: v for k, v in sorted(token_counter.items(), key=lambda item: (-item[1], item[0].lower()))}
                for token in sorted_token_counter:
                    print(str(sorted_token_counter[token]) + "\t" + token)
            i += 1

if __name__ == "__main__":
    result = main()