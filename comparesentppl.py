"""
Compare the per-sentence perplexity of two LMs

Marco Lui, September 2012
"""
import os, sys, argparse
import numpy as np
import rpy
import csv

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="compare the per-sentence complexity of two LMs")
  parser.add_argument('file1')
  parser.add_argument('file2')
  args = parser.parse_args()

  vals1 = np.genfromtxt(args.file1,usecols=(-2,),dtype=float,delimiter=',')
  vals2 = np.genfromtxt(args.file2,usecols=(-2,),dtype=float,delimiter=',')

  ttest = rpy.r['t.test']
  wtest = rpy.r['wilcox.test']

  tres = ttest(vals1, vals2, paired=True)
  wres = wtest(vals1, vals2, paired=True)

  writer = csv.writer(sys.stdout)
  row = (os.path.basename(args.file1), os.path.basename(args.file2))
  row += (tres['estimate']['mean of the differences'], tres['p.value'], wres['p.value'])
  writer.writerow(row)
