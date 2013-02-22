import argparse, bte, chardet, gzip, langid, logging, os, time, urllib, warc

parser = argparse.ArgumentParser()
parser.add_argument('fnames_fname', type=str, 
                    help='filename for a file containing paths to ClueWeb09 files, one per line')
args = parser.parse_args()

outfbase = os.path.basename(args.fnames_fname)
logfname = outfbase + '.log'
fnames = [x.strip() for x in open(args.fnames_fname)]

logging.basicConfig(filename=logfname,filemode='w', level=logging.INFO)

def get_bte_content(wr):
    encoding = chardet.detect(wr.content)['encoding']
    content = wr.content.decode(encoding, errors='replace')
    paragraphs = bte.html2text(content).split('\n')
    return paragraphs

def output_document(docid, title, paragraphs, outf):
    ''' title and paragraphs are assumed to already be encoded appropriately'''
    print >> outf, '<doc id="%d" name="%s">' % (docid, title)
    for p in paragraphs:
        print >> outf, "<p>"
        print >> outf, p
        print >> outf, "</p>"
    print >> outf, "</doc>"

start = time.time()

docid = 1
for f in fnames:
    try:
        outf_en = open(outfbase + '.' + os.path.basename(f) + '.' + 'en' '.vrt', 'w')
        outf_other = open(outfbase + '.' + os.path.basename(f) + '.' + 'other' '.vrt', 'w')
        infile = gzip.open(f)
        for wr in warc.get_warc_responses(infile):
            try:
                if wr.good_doc_for_corpus():
                    paragraphs = get_bte_content(wr)
                    if paragraphs:
                        paragraphs = [p.encode('utf8') for p in paragraphs]
                        uri_encoding = chardet.detect(wr.header['WARC-Target-URI'])['encoding']
                        uri_decoded = wr.header['WARC-Target-URI'].decode(uri_encoding, errors='replace')
                        uri_quoted = urllib.quote(uri_decoded.encode('utf8'))
                        if langid.classify('\n'.join(paragraphs))[0] == 'en':
                            output_document(docid, uri_quoted, paragraphs, outf_en)
                        else:
                            output_document(docid, uri_quoted, paragraphs, outf_other)
                        docid += 1
            except Exception, e:
                logging.warn("Error for warc response for %s: %s" % (wr.header['WARC-TREC-ID'],e.message))
                continue
        infile.close()
        logging.info('Finished %s' % f)
        outf_en.close()
        outf_other.close()
    except Exception, e:
        logging.warn('Error for file %s: %s' % (f,e.message))
        outf_en.close()
        outf_other.close()
        continue

logging.info('Finished %s' % args.fnames_fname)

end = time.time()
logging.info("Time elapsed: %f" % (end - start))
