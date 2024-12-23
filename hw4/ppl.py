import re
from collections import defaultdict
import argparse
import math

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--sentences', type=str, required=True, help='sentences')
arg_parser.add_argument('--lm', type=str, required=True, help='language model')
arg_parser.add_argument('--l1', type=str, required=True, help='sentences')
arg_parser.add_argument('--l2', type=str, required=True, help='sentences')
arg_parser.add_argument('--l3', type=str, required=True, help='sentences')
args = arg_parser.parse_args()

def main():
    with open(args.lm, 'r') as lm:
        with open(args.sentences, 'r') as sentences:
            generator = PPLGenerator(lm, args.l1, args.l2, args.l3)
            # for entry in generator.lm:
            #     print(entry)
            generator.generate(sentences)

class PPLGenerator:
    def __init__(self, lm: str, l1: str, l2: str, l3: str):
        self.lambdas = (float(l1), float(l2), float(l3))
        self.lm = self.load_lm(lm)

    def load_lm(self, lm: str) -> defaultdict:
        lm_map = defaultdict(list)
        for line in lm:
            if line.startswith("\\") or line.startswith("ngram"):
                continue
            else:
                pieces = line.strip().split()
                if len(pieces) < 4:
                    continue
                count, prob, logprob = pieces[0], pieces[1], pieces[2]
                words = tuple(pieces[3:])
                lm_map[words] = (count, prob, logprob)
        return lm_map
    
    def generate(self, sentences: str) -> None:
        prob_sum, word_num, oov_num, sent_num = 0, 0, 0, 0
        for sentence in sentences:
            sent_num += 1
            new_prob_sum, new_word_num, new_oov_num = self.process_sentence(sentence, sent_num)
            prob_sum += new_prob_sum
            word_num += new_word_num
            oov_num += new_oov_num
        count = word_num + sent_num - oov_num
        ave_logprob = prob_sum / count
        ppl = 10**(-1 * ave_logprob)
        print(f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(f"sent_num={sent_num} word_num={word_num} oov_num={oov_num}")
        print(f"lgprob={prob_sum} ave_lgprob={ave_logprob} ppl={ppl}")

    def process_sentence(self, sentence: str, sent_num: int) -> tuple[int, int, int]:
        l1, l2, l3 = self.lambdas
        prob_sum, word_num, oov_num = 0, 0, 0
        sentence = f"<s> {sentence.strip()} </s>"
        tokenized_sentence = [token for token in re.findall(r"\S+", sentence)]
        print(f"Sent #{sent_num}: {sentence}")
        for i in range(1, len(tokenized_sentence)):
            word = tokenized_sentence[i]
            if word not in ('<s>', '</s>'):
                word_num += 1
            unseen = False
            prev_word = tokenized_sentence[i - 1]
            prev_prev_word = tokenized_sentence[i - 2] if i - 2 >= 0 else ""
            prev_words = prev_prev_word + " " + prev_word if i > 1 else prev_word
            if self.isKnown(word):
                prob_w = float(self.lm[tuple([word])][1])
                if (prev_word, word) in self.lm:
                    prob_pw = float(self.lm[(prev_word, word)][1])
                else:
                    prob_pw = 0
                    unseen = True
                if i > 1:
                    if (prev_prev_word, prev_word, word) in self.lm:
                        prob_ppw = float(self.lm[(prev_prev_word, prev_word, word)][1])
                    else:
                        prob_ppw = 0
                        unseen = True
                else:
                    prob_ppw = 0
                total_prob = (l1 * prob_w) + (l2 * prob_pw) + (l3 * prob_ppw)
                log_prob = math.log10(total_prob)
                prob_sum += log_prob
                if unseen:
                    print(f"{i}: lg P({word} | {prev_words}) = {log_prob} (unseen ngrams)")
                else:
                    print(f"{i}: lg P({word} | {prev_words}) = {log_prob}")
            else:
                oov_num += 1
                print(f"{i}: lg P({word} | {prev_words}) = -inf (unknown word)")
        count = word_num + 1 - oov_num
        ave_logprob = prob_sum / count
        ppl = 10**(-1 * ave_logprob)
        print(f"1 sentence, {word_num} words, {oov_num} OOVs")
        print(f"lgprob={prob_sum} ppl={ppl}\n")
        return prob_sum, word_num, oov_num

    def isKnown(self, word: str) -> bool:
        return tuple([word]) in self.lm

if __name__ == "__main__":
    result = main()