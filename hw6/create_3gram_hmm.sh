#!/bin/sh
if [ $# -ne 5 ]; then
    echo "Usage: $0 <output_file>"
    exit 1
fi

output=$1
l1=$2
l2=$3
l3=$4
unkprobs=$5

/mnt/dropbox/24-25/570/envs/570/bin/python create_3gram_hmm.py --l1 "$l1" --l2 "$l2" --l3 "$l3" --unkprobs "$unkprobs" > "$output"
