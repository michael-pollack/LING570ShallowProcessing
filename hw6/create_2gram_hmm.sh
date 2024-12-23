#!/bin/sh
if [ $# -ne 1 ]; then
    echo "Usage: $0 <output_file>"
    exit 1
fi

output=$1

/mnt/dropbox/24-25/570/envs/570/bin/python create_2gram_hmm.py > "$output"
