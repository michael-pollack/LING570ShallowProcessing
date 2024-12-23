#!/bin/sh
if [$# -ne 6]; then
    echo "Usage: $0 <training> <ngram> <sentences> <lm> <l1> <l2> <l3> <output_file>"
    exit 1
fi

training=$1
ngram=$2
sentences=$3
lm=$4
l1=$5
l2=$6
l3=$7
output=$8

/mnt/dropbox/24-25/570/envs/570/bin/python ngram_count.py --input $training > $ngram
/mnt/dropbox/24-25/570/envs/570/bin/python build_lm.py --input $ngram > $lm
/mnt/dropbox/24-25/570/envs/570/bin/python ppl.py --sentences $sentences --lm $lm --l1 $l1 --l2 $l2 --l3 $l3 > $output