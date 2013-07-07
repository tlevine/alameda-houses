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

def parse(filename):
    # filename = open(os.path.join('results', apn), 'r')
    html = lxml.html.parse(filename)

    html.xpath('id("pplresultcontent3")/tr[position()=3]/td[position()>1]/text()')
    texts = html.xpath('id("pplresultcontent3")/tr[position()=3]/td[position()>1]/text()')
    property_address = '\n'.join(filter(None, [line.strip() for line in texts]))

    return html
