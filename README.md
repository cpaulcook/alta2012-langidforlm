Code accompanying alta2012-langidforlm
==============================================

This repository contains code to reproduce experiments from the
following paper:

Paul Cook and Marco Lui. langid.py for better language modelling. In
Proceedings of the Australasian Language Technology Association
Workshop 2012 (ALTA 2012), pages 107–112. Dunedin, New Zealand.

The paper is available from:
http://aclweb.org/anthology-new/U/U12/U12-1014.pdf

Requirements
------------

Jan Pomikalek's implementation of BTE: 
http://nlp.fi.muni.cz/~xpomikal/cleaneval/bte-3.0/bte.py

langid.py: https://github.com/saffsd/langid.py

Onion: http://code.google.com/p/onion/

StanfordNLP tools: http://www-nlp.stanford.edu/

ClueWeb09: http://www.lemurproject.org/clueweb09/

SRILM: http://www.speech.sri.com/projects/srilm/

GNU Parallel: http://www.gnu.org/software/parallel/


Building ClueWeb corpora
------------------------
To build the ClueWeb corpora, first create a file containing the paths
to the first 100 files in English ClueWeb. Then run 

# python extractvertcorporaforlangidexps.py FILE_OF_CLUEWEB_FILENAMES

(This takes a while...)

This creates 1 file per ClueWeb filename. The files are in vertical
format (token-per-line), whitespace separated. The "en" files contain
documents langid.py thinks are English, the "other" files contain
other languages.

Cat the extracted files together in various combinations. For the
paper we did the first 1, 5, 10, 50, 100 files, and just "en" and
"en"+"other". (So we created 10 files in total.)

(If you just want an English corpus from ClueWeb, and don't care about
reproducing our experiments, just cat all the "en" files into one
file at this stage.)

The next step is to put the files just created through the rest of the
corpus processing pipeline (to take care of deduplication, sentence
splitting, tokenisation, and getting rid of sentences with really long
tokens that seemed to trip up SRILM).

The path to the stanford NLP tools is hardcodede in
`wsvert2srilm.bash`. The path to Onion is hard-coded in
`runonion.bash`. You'll (probably) need to fix those accordingly.

Then run 

# wsvert2srilm.bash FILE

This script creates files in sentence-per-line format, with tokens
separated by whitespace.

Language Modelling and perplexity calculation
---------------------------------------------

We use SRILM to implement our language models and to compute perplexity.
Model construction proceeds in several steps. 

Token counts
~~~~~~~~~~~~

The corpora are large enough such that `ngram-count` will not be able to operate
on the whole corpus at once, so we split the corpora up, and then use srilm's 
make-batch-counts and merge-batch-counts. 

We split each file into lines of 1000000 lines::

  mkdir 00-99.all.split; split -l 1000000 ../data/clueweblangid_corpora/00-99.all.srilm 00-99.all.split/00-99.all.
  mkdir 00-99.en.split; split -l 1000000 ../data/clueweblangid_corpora/00-99.en.srilm 00-99.en.split/00-99.en.

We then do the counting using make-batch-counts
# mkdir 00-99.all.counts; make-batch-counts <(find 00-99.all.split -type f) 10 /bin/cat 00-99.all.counts
# mkdir 00-99.en.counts; make-batch-counts <(find 00-99.en.split -type f) 10 /bin/cat 00-99.en.counts
 
We then merge them
# merge-batch-counts 00-99.all.counts
# merge-batch-counts 00-99.en.counts
 
Build lms using `make-big-lm`:

# find . -name '*.count' | parallel -j1 "make-big-lm -name {/.}.model -read {} -unk -lm {/.}.defaults.lm"
# find -L . -maxdepth 1 -type f -name '*.gz' |  parallel -j1 "make-big-lm -name {/.}.model -read {} -unk -lm {/.}.defaults.lm"

Run all the lms against brown:
# find . -maxdepth 1 -type f  -name '*.lm' | parallel -j1 "echo {};ngram -ppl ../data/clueweblangid_corpora/brown.srilm -unk -lm {};echo {}"
# find . -maxdepth 1 -type f  -name '*.lm' | parallel -j1 "echo {};ngram -ppl ../data/clueweblangid_corpora/bnc.written.srilm -unk -lm {};echo " > bnc.written.ppl
# ./run_lms.sh

Low-order language models
~~~~~~~~~~~~~~~~~~~~~~~~~
Build lower-order LMS:
# find -L . -maxdepth 1 -type f -name '00.*.count.gz' |  parallel -j2 "make-big-lm -name {/.}.model -read {} -unk -order 2 -lm {/.}.order2.lm"
# find -L . -maxdepth 1 -type f -name '00.*.count.gz' |  parallel -j2 "make-big-lm -name {/.}.model -read {} -unk -order 1 -lm {/.}.order1.lm"

Apply the lower-order LMS to bnc
# parallel -j1 "echo {};ngram -ppl ../data/clueweblangid_corpora/bnc.written.srilm -unk -order 2 -lm {};echo " ::: *order2* > bnc.written.order2.ppl
# parallel -j1 "echo {};ngram -ppl ../data/clueweblangid_corpora/bnc.written.srilm -unk -order 1 -lm {};echo " ::: *order1* > bnc.written.order1.ppl

Sentence-level perplexity
~~~~~~~~~~~~~~~~~~~~~~~~~
Run all the web LMS against bnc.written.delim:
# parallel "ngram -escape STARTDOC -ppl ../data/clueweblangid_corpora/bnc.written.delim.srilm -unk -lm {} > sentppl/{/.}.sentppl" ::: 00*.defaults.lm

Tabulate all the sentence-level ppls:
# find sentppl -name '*.sentppl' | parallel "python sentppl.py {} > {.}.csv"

Compute all p-values pairwise
# parallel --xapply python comparesentppl.py {1} {2} :::: <(ls sentppl/*all*.csv) <(ls sentppl/*en*.csv) > significance.csv

Multiple-small LM
~~~~~~~~~~~~~~~~~
Compute counts for each file
# find -L ../data/clueweblangid_corpora -name '*.srilm' | parallel "if [ ! -e {/.}.count.gz ];then ngram-count -text {} -write {/.}.count;gzip {/.}.count;fi"

Build the LMS
# parallel echo 0{2}.{1}.count.gz ::: all en :::: <(seq 1 9) | parallel -j8 "make-big-lm -name {/.}.model -read {} -unk -lm {/.}.defaults.lm"

Apply the LMS
# parallel echo 0{2}.{1}.count.defaults.lm ::: all en :::: <(seq 1 9) | parallel -j2 "echo {};ngram -ppl ../data/clueweblangid_corpora/bnc.written.srilm -unk -lm {};echo " > bnc.written.smallLM.ppl
# parallel echo 0{2}.{1}.count.defaults.lm ::: all en ::: 0 | parallel -j2 "echo {};ngram -ppl ../data/clueweblangid_corpora/bnc.written.srilm -unk -lm {};echo " >> bnc.written.smallLM.ppl
# python LMout2csv.py bnc.written.smallLM.ppl > bnc.written.smallLM.ppl.csv
