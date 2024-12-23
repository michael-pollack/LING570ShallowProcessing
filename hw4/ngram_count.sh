#!/bin/sh
if [$# -ne 3]; then
    echo "Usage: $0 <training_file> <output_file>"
    exit 1
fi

input=$1
output=$2

/mnt/dropbox/24-25/570/envs/570/bin/python ngram_count.py --input $input > $output
