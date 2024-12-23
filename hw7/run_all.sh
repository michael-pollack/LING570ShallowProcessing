#!/bin/bash

for i in {1..5}
do
  # File names
  hmm="hmm$i"
  test_file="test.word"
  sys="sys$i"
  dir="./examples"

  # Run viterbi.sh
  tt=$( { time -p ./viterbi.sh "$dir"/"$hmm" "$dir"/"$test_file" "$sys"; } 2>&1 | awk '/real/ {print $2}' )

  # Run conv_format.sh
  cat "$sys" | ./conv_format.sh > "$sys"_res

  # Run calc_tagging_accuracy.pl
  "$dir"/calc_tagging_accuracy.pl "$dir"/"$test_file"_pos "$sys"_res > "$sys"_res.acc 2>&1

  # Print accuracy
  accuracy=$(awk '/accuracy/ {print $2}' "$sys"_res.acc)
  echo "Accuracy for $hmm: $accuracy took $tt seconds"
done