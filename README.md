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
http://nlp.fi.muni.cz/-xpomikal/cleaneval/bte-3.0/bte.py

langid.py: https://github.com/saffsd/langid.py

Onion: http://code.google.com/p/onion/

StanfordNLP tools: http://www-nlp.stanford.edu/

ClueWeb09: http://www.lemurproject.org/clueweb09/

SRILM: http://www.speech.sri.com/projects/srilm/

Building ClueWeb corpora
========================
To build the ClueWeb corpora, first create a file containing the paths
to the first 100 files in English ClueWeb. Then run

    python extractvertcorporaforlangidexps.py FILE_OF_CLUEWEB_FILENAMES

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
``wsvert2srilm.bash``. The path to Onion is hard-coded in
``runonion.bash``. You'll (probably) need to fix those accordingly,
then run 

    wsvert2srilm.bash FILE

This script creates files in sentence-per-line format, with tokens
separated by whitespace.

Language Modelling and perplexity calculation
=============================================

We use SRILM to implement our language models and to compute perplexity.
Model construction proceeds in several steps. 

Token counts
------------

The corpora are large enough such that ``ngram-count`` will not be able to operate
on the whole corpus at once, so we split the corpora up, and then use srilm's 
make-batch-counts and merge-batch-counts. Below is a rough guide on how
to do this, for more details see the SRILM documentation

    # split each file into lines of 1000000 lines:
    mkdir FILE.split; split -l 1000000 FILE FILE.split/part.

    # do counting for each part using make-batch-counts:
    mkdir FILE.counts; make-batch-counts <(find FILE.split -type f) 10 /bin/cat FILE.counts
 
    # merge counts
    merge-batch-counts FILE.counts
 
    # build lms using `make-big-lm`
    make-big-lm -name FILE.model -read FILE.counts -unk -lm FILE.lm
    
    # compute perplexity
    ngram -ppl TARGET -unk -lm FILE.lm

In the included file ``run_lms.sh`` is our code for computing the perplexity
on each target data using each of the language models we trained. ``LMout2csv.py``
parses the SRILM stdout into a csv format more amenable to further analysis.

Sentence-level perplexity
-------------------------
We do calculations of perplexity at a sentence level as well. To do this using SRILM,
the approach is as follows:

    ngram -escape STARTDOC -ppl EVAL_DATA -unk -lm FILE.lm > EVAL_DATA.FILE_lm.sentppl

We include ``sentppl.py``, a script to parse the raw STDOUT of the above type of
SRILM command and produce a CSV format.

Finally, we compare the per-sentence perplexity of two LMs, computing a p-value
using a t-test as well as a Wilcoxon signed-rank test. We provide a script
``comparesentppl.py`` to carry out this process, which again produces a CSV-format
output.

