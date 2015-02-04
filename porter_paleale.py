#!/usr/bin/env python
"""
A client to query the Porter, Pale Ale 4.0

Porter is a server for protein secondary structure prediction based on an
ensemble of 25 BRNNs (bidirectional recurrent neural networks).

PaleAle is a server for the prediction of protein relative solvent
accessibility.

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

Server documentation: http://distillf.ucd.ie/porterpaleale/quickhelp.html
"""
import re
import requests
import time
import sys


API_ENDPOINT = (
    "http://distillf.ucd.ie/~distill/cgi-bin/distill/predict_porterpaleale")


class Prediction:
    """
    Hold information regarding Porter and Pale Ale predictions
    """
    def __init__(self, sequence, secondary_structure, solvent_accessibility):
        self.sequence = sequence
        self.secondary_structure = secondary_structure
        self.solvent_accessibility = solvent_accessibility

    def __repr__(self):
        return "{}\n{}\n{}\n".format(
            self.sequence,
            self.secondary_structure,
            self.solvent_accessibility
        )


def _retrieve_prediction_results(prediction_url, wait):
    """
    Fetch results from a given prediction

    :param prediction_url: URL where the results are available
    :param wait: Time to wait before retrying to fetch results

    :return: Prediction containing secondary structure and
        solvent accessibiltity
    """
    prediction = None
    results = ''
    while 'complete' not in results:
        time.sleep(wait)
        results = requests.get(prediction_url).text
    if results:
        results = re.findall('Query_length:.*?\n\n(.*?)\n\n\n', results, re.S)
        results = results[0].split('\n')
        prediction = Prediction(*results)
    return prediction


def predict(sequence, wait=2):
    """
    Predict secondary structure and solvent accessibility for a given
    aminoacid sequence

    :param sequence: A string containing the sequence to be predicted
    :param wait: Time to wait before retrying to fetch results

    :return: Prediction containing secondary structure and
        solvent accessibiltity
    """
    response = requests.post(
        API_ENDPOINT, {'input_text': '>Sequence\n' + sequence})
    prediction = None
    try:
        response.raise_for_status()
        links = re.findall(
            'href=[\'"]?([^\'" >]+)',
            response.text
        )
        if links:
            prediction_url = links[0]
            prediction = _retrieve_prediction_results(prediction_url, wait)
    except:
        raise Exception(
            "Could not fetch results from Porter Pale Ale 4.0 ({}, {})".format(
                response.status_code, response.text)
        )

    return prediction


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Syntax: porter_paleale.py <sequence>")
    else:
        print(predict(sys.argv[1]))
