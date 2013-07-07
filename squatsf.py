from collections import OrderedDict

from lxml.html import fromstring

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

from dumptruck import DumpTruck

dt = DumpTruck('squatsf.db')

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
    dt.upsert(OrderedDict([('apn', apn), ('html', r.text)]), 'squatsf')
    dt.create_index(['apn'], 'squatsf', if_not_exists = True, unique = True)

def parse(apn):
    dt.execute("SELECT 'html'
    html = fromstring(r.text)
    return html
