#!/bin/sh
if [$# -ne 6]; then
    echo "Usage: $0 <lm> <l1> <l2> <l3> <sentences> <output_file>"
    exit 1
fi

lm=$1
l1=$2
l2=$3
l3=$4
sentences=$5
output=$6

/mnt/dropbox/24-25/570/envs/570/bin/python ppl.py --sentences "$sentences" --lm $lm --l1 $l1 --l2 $l2 --l3 $l3 > $output
