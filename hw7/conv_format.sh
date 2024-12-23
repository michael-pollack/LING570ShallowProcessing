#!/bin/sh
if [ $# -ne 0 ]; then
    echo "Usage: $0 <hmm_file> <observation_file>"
    exit 1
fi

/mnt/dropbox/24-25/570/envs/570/bin/python conv_format.py