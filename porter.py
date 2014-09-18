#!/usr/bin/env python
"""
Porter 4.0 client

Quick explanation of output formats

Porter (Secondary Structure):
    H = Helix   (DSSP classes H, G and I)
    E = Strand  (DSSP classes E and B)
    C = Coil    (DSSP classes S, T and .)

PaleAle (Relative Solvent Accessibility):
    B = very buried      (<=4% accessible)
    b = somewhat buried  (>4% and <=25% accessible)
    e = somewhat exposed (>25% and <=50% accessible)
    E = very exposed     (>50% accessible)
"""
import re
import requests
import time
from bs4 import BeautifulSoup
import sys


class Porter4(object):

    QUERY_API_ENDPOINT = "http://distillf.ucd.ie/~distill/cgi-bin/distill/predict_porterpaleale"

    @classmethod
    def query(cls, sequence):
        response = requests.post(cls.QUERY_API_ENDPOINT, {'input_text': '>Sequence\n' + sequence})
        results = ''
        if response.status_code == 200:
            results_url = BeautifulSoup(response.text).a['href']
            while 'complete' not in results:
                results = requests.get(results_url).text
                time.sleep(2)
            results =  "".join(re.findall("Query_length:.*?\n\n(.*?)\n\n\n", results, re.S))
        else:
            raise Exception("Could not submit query to the Porter server (error {})".format(response.status_code)) 

        return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("You must enter your sequence")
    else:
        print(Porter4.query(sys.argv[1]))
