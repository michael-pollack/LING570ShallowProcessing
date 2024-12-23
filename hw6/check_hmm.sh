#!/bin/sh
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

input=$1

/mnt/dropbox/24-25/570/envs/570/bin/python check_hmm.py --input $input