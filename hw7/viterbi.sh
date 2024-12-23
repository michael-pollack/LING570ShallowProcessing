#!/bin/sh
if [ $# -ne 2 ]; then
    echo "Usage: $0 <hmm_file> <observation_file>"
    exit 1
fi

hmm=$1
obs=$2

/mnt/dropbox/24-25/570/envs/570/bin/python viterbi_redux.py --hmm $hmm --input $obs