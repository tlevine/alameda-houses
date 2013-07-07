import os
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

TAX_KEYS = [None, 'tax-type', 'bill-year', 'tracer', 'total-amount', None]
INSTALLMENT_KEYS = [None, 'installment', 'due-date', None, 'installment-amount', 'status', 'status-date']
def _parse_row(mainrow, installments):
    row = dict(zip(TAX_KEYS, mainrow.xpath('td/text()')))
    del row[None]
    row["total-amount"] = float(row["total-amount"].replace('$', '').replace(',', ''))
    row["installments"] = []
    for installment in installments:
        subrow = dict(zip(INSTALLMENT_KEYS, installment.xpath('td/text()')))
        del subrow[None]
        row['installments'].append(subrow)
    return row

def parse(filename):
    # filename = open(os.path.join('results', apn), 'r')
    html = lxml.html.parse(filename)

    html.xpath('id("pplresultcontent3")/tr[position()=3]/td[position()>1]/text()')
    texts = html.xpath('id("pplresultcontent3")/tr[position()=3]/td[position()>1]/text()')



    information = []
    table = html.xpath('id("pplresultcontent4")')[0]
    # keys = [k.replace(' ', '-').lower() for k in mainrow.xpath('td[position()>1 and position() < last()]/text()')]
    table.xpath('tr[position()=1]/td[position()>1 and position() < last()]/text()')
    for tr in table.xpath('tr[position()>1)'):
        for td in tr.xpath('td'):
            pass


    return {
        "apn": html.xpath('id("pplresultcontent3")/tr[position()=2]/td[position()=2]/text()')[0].strip(),
        "property-address": '\n'.join(filter(None, [line.strip() for line in texts])),
        "information": information,
    }
