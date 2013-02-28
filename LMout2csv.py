#!env python
import csv, argparse, os, re, sys

R_FILE = re.compile(r"file (?P<path>\S*): (?P<sentences>\S*) sentences, (?P<words>\S*) words, (?P<oovs>\d+) OOVs")
R_PROB = re.compile(r"(?P<zeroprobs>\d+) zeroprobs, logprob= (?P<logprob>\S+) ppl= (?P<ppl>\S+) ppl1= (?P<ppl1>\S+)")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Process SRILM ppl output into CSV")
  parser.add_argument('infile', type=str)

  args = parser.parse_args()

  writer = csv.writer(sys.stdout)
  with open(args.infile) as f:
    for row in f:
      if row.strip().endswith('.lm'):
        lm_filename = os.path.basename(row.strip())
      elif R_FILE.match(row):
        m = R_FILE.match(row)
        eval_filename = os.path.basename( m.group('path') )
      elif R_PROB.match(row):
        m = R_PROB.match(row)
        zeroprobs = eval(m.group('zeroprobs'))
        logprob = eval(m.group('logprob'))
        ppl = eval(m.group('ppl'))
        ppl1 = eval(m.group('ppl1'))
        writer.writerow((lm_filename, eval_filename, zeroprobs, logprob, ppl, ppl1))
      elif not row.strip():
        pass
      else:
        raise ValueError(row)
