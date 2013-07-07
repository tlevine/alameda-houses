import os, datetime
from collections import OrderedDict

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

import lxml.html

class HTTPSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

def search(apn):
    s = Session()
    s.mount('https://', HTTPSAdapter())
    url = 'https://www.acgov.org/ptax_pub_app/RealSearch.do'
    data = {
        'displayApn': apn,
        'situsStreetNumber': '',
        'situsStreetName': '',
        'situsStreetSuffix': '',
        'situsUnitNumber': '',
        'situsCity': '',
        'searchBills': 'Search',
        'showHistory': 'N',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    }
    s.get('https://www.acgov.org/ptax_pub_app/RealSearchInit.do?showSearchParmsFromLookup=true', headers = headers)
    r = s.post(url, data = data)
    try:
        os.mkdir('results')
    except OSError:
        pass

    f = open(os.path.join('results', apn), 'w')
    f.write(r.text)
    f.close()

def _money(raw):
    return float(raw.replace('$', '').replace(',', ''))

TAX_KEYS = [None, 'tax-type', 'bill-year', 'tracer', 'total-amount', None]
INSTALLMENT_KEYS = [None, 'installment', 'due-date', None, 'installment-amount', 'status/status-date']
def _parse_row(mainrow, installments):
    row = dict(zip(TAX_KEYS, mainrow.xpath('td/text()')))

    row["total-amount"] = _money(row["total-amount"])
    row["installments"] = []

    del row[None]

    for installment in installments:
        subrow = dict(zip(INSTALLMENT_KEYS, installment.xpath('td/text()')))

        subrow['due-date'] = datetime.datetime.strptime(
            subrow['due-date'].strip(), '%m/%d/%Y').date().isoformat()

        subrow['status'] = subrow['status/status-date'].split(' ')[0]
        subrow['status-date'] = datetime.datetime.strptime(
            subrow['status/status-date'].strip(),
            subrow['status'] + ' %b %d, %Y').date().isoformat()

        subrow['installment'] = int(filter(lambda char: char in '1234567890', subrow['installment']))
        subrow['installment-amount'] = _money(subrow['installment-amount'])

        del subrow[None]
        del subrow['status/status-date']
        row['installments'].append(subrow)
    return row

def parse(filename):
    # filename = open(os.path.join('results', apn), 'r')
    html = lxml.html.parse(filename)

    html.xpath('id("pplresultcontent3")/tr[position()=3]/td[position()>1]/text()')
    texts = html.xpath('id("pplresultcontent3")/tr[position()=3]/td[position()>1]/text()')



    information = []
    table = html.xpath('id("pplresultcontent4")')[0]
    for tr in table.xpath('tr'):
        if tr.attrib['class'] == 'pplbilldivider':
            if mainrow != None and installments != []:
                information.append(_parse_row(mainrow, installments))

            mainrow = None
            installments = []
        elif mainrow == None:
            mainrow = tr
        else:
            installments.append(tr)

    return {
        "apn": html.xpath('id("pplresultcontent3")/tr[position()=2]/td[position()=2]/text()')[0].strip(),
        "property-address": '\n'.join(filter(None, [line.strip() for line in texts])),
        "information": information,
    }
