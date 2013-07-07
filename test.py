#!/usr/bin/env python
import os
import json

import nose.tools as n

import houses

def check_parse(apn):
    observed = houses.parse(os.path.join('fixtures', apn, 'input'))
    expected = json.load(open(os.path.join('fixtures', apn, 'output')))
    n.assert_equal(observed, expected)

def test_parse():
    for apn in os.listdir('fixtures'):
        yield check_parse, apn
