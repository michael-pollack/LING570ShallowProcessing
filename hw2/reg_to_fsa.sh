#!/bin/sh
if [$# -ne 3]; then
    echo "Usage: $0 <grammar_file> <output_file>"
    exit 1
fi

/mnt/dropbox/24-25/570/envs/570/bin/python reg_to_fsa.py
