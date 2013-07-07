#!/usr/bin/env python
import os
import json

import nose.tools as n
import lxml.html

import houses


def test_parse_row():
    'An individual row should be parsed correctly.'
    mainrow = lxml.html.fromstring('''
                        <tr class=pplevenrow>
                            <td align="left" width="3%">&nbsp;</td>
                            <td align="left" width="24%">Secured</td>
                            <td align="left" width="15%">2012-2013</td>
                            <td align="left" width="15%">36178700</td>
                            <td align="left" width="15%">$5,837.64</td>
                            <td align="left" width="25%">&nbsp;

                                    <a href="/ptax_pub_app/PublicDownload.do?getStreamInfo=true&amp;pubCurrRollYear=2012&amp;pubBillType=SEC&amp;pubBillId=36178700" tabindex="3" class="pplviewbill">View Bill</a>

                                &nbsp;&nbsp;&nbsp;&nbsp;

                            </td>
                            <td align="left" width="3%">&nbsp;</td>
                        </tr>
    ''')
    installments = [
        lxml.html.fromstring('''
                        <tr class=pplevenrow>
                            <td align="left" width="3%">&nbsp;</td>
                            <td align="center" width="24%">1st Installment</td>
                            <td align="right" width="15%">12/10/2012&nbsp;&nbsp;</td>
                            <td align="left" width="15%">&nbsp;</td>
                            <td align="right" width="15%">$2,918.82</td>
                            <td align="right" width="28%" colspan="2">Paid Nov 5, 2012&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                        </tr>
        '''),
        lxml.html.fromstring('''
                        <tr class=pplevenrow>
                            <td align="left" width="3%">&nbsp;</td>
                            <td align="center" width="24%">2nd Installment</td>
                            <td align="right" width="15%">04/10/2013&nbsp;&nbsp;</td>
                            <td align="left" width="15%">&nbsp;</td>
                            <td align="right" width="15%">$2,918.82</td>
                            <td align="right" width="28%" colspan="2">Paid Mar 8, 2013&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                        </tr>
        ''')
    ]


    observed = houses._parse_row(mainrow, installments)
    expected = {
      "tax-type": "Secured",
      "bill-year": "2012-2013",
      "tracer": "36178700",
      "total-amount": 5837.64,
      "installments": [
        {
          "installment": 1,
          "due-date": "2012-12-10",
          "installment-amount": 2918.82,
          "status": "Paid",
          "status-date": "2012-11-05"
        },
        {
          "installment": 2,
          "due-date": "2013-04-10",
          "installment-amount": 2918.82,
          "status": "Paid",
          "status-date": "2013-03-08"
        }
      ]
    }
    n.assert_equal(observed, expected)

def check_parse(apn):
    observed = houses.parse(os.path.join('fixtures', apn, 'input'))
    expected = json.load(open(os.path.join('fixtures', apn, 'output')))
    n.assert_equal(observed, expected)

@n.nottest
def test_parse():
    for apn in os.listdir('fixtures'):
        yield check_parse, apn
