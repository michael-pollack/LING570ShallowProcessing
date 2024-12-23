#!/bin/sh
if [$# -ne 3]; then
    echo "Usage: $0 <grammar_file> <output_file>"
    exit 1
fi

fst=$1
input=$2

/mnt/dropbox/24-25/570/envs/570/bin/python fst_acceptor.py --fst "$fst" --input "$input"
