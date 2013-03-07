#!env python
"""
Tabulation of sentence-level perplexity
"""
import csv, argparse, os, re, sys

R_SENT = re.compile(r"(?P<sentences>\S*) sentences, (?P<words>\S*) words, (?P<oovs>\d+) OOVs")
R_FILE = re.compile(r"file (?P<path>\S*): (?P<sentences>\S*) sentences, (?P<words>\S*) words, (?P<oovs>\d+) OOVs")
R_PROB = re.compile(r"(?P<zeroprobs>\d+) zeroprobs, logprob= (?P<logprob>\S+) ppl= (?P<ppl>\S+) ppl1= (?P<ppl1>\S+)")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Process SRILM ppl output into CSV")
  parser.add_argument('infile', type=str)

  args = parser.parse_args()

  writer = csv.writer(sys.stdout)
  sent_index = 0
  with open(args.infile) as f:
    for row in f:
      if row.strip() == 'STARTDOC':
        sent_index += 1
      elif R_SENT.match(row):
        m = R_SENT.match(row)
        sent_count = m.group('sentences')
        word_count = m.group('words')
      elif R_PROB.match(row):
        m = R_PROB.match(row)
        zeroprobs = eval(m.group('zeroprobs'))
        logprob = eval(m.group('logprob'))
        ppl = eval(m.group('ppl'))
        ppl1 = eval(m.group('ppl1'))
        writer.writerow(('sent{0:05}'.format(sent_index), sent_count, word_count, zeroprobs, logprob, ppl, ppl1))
      elif not row.strip():
        pass
      elif R_FILE.match(row):
        # end-of-file, no more sentences. This is the summary.
        break
      else:
        raise ValueError(row)
