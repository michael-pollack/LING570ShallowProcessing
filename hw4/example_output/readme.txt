"ppl_0.2_0.5_0.3" contains the expected content for the first sentence after running the following commands:

./ngram_count.sh 570/hw4/examples/wsj_sec0_19.word wsj_sec0_19.ngram_count

./build_lm.sh wsj_sec0_19.ngram_count wsj_sec0_19.lm

./ppl.sh wsj_sec0_19.lm 0.2 0.5 0.3 570/hw4/examples/wsj_sec22.word ppl_0.2_0.5_0.3

