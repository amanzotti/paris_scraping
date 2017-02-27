import requests
from bs4 import BeautifulSoup
import sys
import numpy as np
# then add this function lower down
from memory_profiler import profile


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_pap():
    base = 'http://www.pap.fr/annonce/locations-appartement-paris-14e-g37781'
    resp = requests.get(base, timeout=10)
    resp.raise_for_status()  # <- no-op if status==200
    resp_comb = resp.content
    for i in [13, 14]:
        print(i)
        base2 = 'http://www.pap.fr/annonce/locations-appartement-paris-{}e-g37781'.format(i)
        resp_ = requests.get(base2, timeout=10)
        # resp_.raise_for_status()  # <- no-op if status==200
        if resp_.status_code == 404:
            break
        parsed = parse_source(resp_.content, resp_.encoding)
        listing = extract_listings_pap(parsed)
        print(listing)
        resp_comb += resp_.content + resp_comb

        for j in np.arange(1, 2):
            print(j)
            base2 = 'http://www.pap.fr/annonce/locations-appartement-paris-{}e-g37781-{}'.format(
                i, j)
            resp_ = requests.get(base2, timeout=10)
            # resp_.raise_for_status()  # <- no-op if status==200
            if resp_.status_code == 404:
                break
            resp_comb += resp_.content + resp_comb

    return resp_comb, resp.encoding


def fetch_fusac():
    base = 'http://ads.fusac.fr/ad-category/housing/'
    resp = requests.get(base, timeout=10)
    resp.raise_for_status()  # <- no-op if status==200
    resp_comb = resp.content
    for i in np.arange(0, 6):
        print(i)
        base2 = 'http://ads.fusac.fr/ad-category/housing/page/{}/'.format(i)
        resp_ = requests.get(base2, timeout=10)
        # resp_.raise_for_status()  # <- no-op if status==200
        if resp_.status_code == 404:
            break
        resp_comb += resp_.content + resp_comb
    return resp_comb, resp.encoding

# handle response 200


def fetch_search_results(
    query=None, minAsk=600, maxAsk=1450, bedrooms=None, bundleDuplicates=1,
    pets_cat=1
):
    search_params = {
        key: val for key, val in locals().items() if val is not None
    }
    if not search_params:
        raise ValueError("No valid keywords")

    base = 'https://paris.craigslist.fr/search/apa'
    resp = requests.get(base, params=search_params, timeout=3)
    resp.raise_for_status()  # <- no-op if status==200
    return resp.content, resp.encoding


# def extract_listings(parsed):
#     listings = parsed.find_all("li", {"class": "result-row"})
#     return listings

def extract_listings_fusac(parsed):
    # location_attrs = {'data-latitude': True, 'data-longitude': True}
    listings = parsed.find_all(
        'div', {'class': "prod-cnt prod-box shadow Just-listed"})
    extracted = []

    for listing in listings[0:]:
        # hood = listing.find('span', {'class': 'result-hood'})
        # # print(hood)
        # # location = {key: listing.attrs.get(key, '') for key in location_attrs}
        # link = listing.find('a', {'class': 'result-title hdrlnk'})  # add this
        # if link is not None:
        #     descr = link.string.strip()
        #     link_href = link.attrs['href']

        price = listing.find('p', {'class': 'post-price'})
        if price is not None:
            price = float(price.string.split()[0].replace(',', ''))

        # link = listing.find('div', {'class': 'listos'}).find('a',href=True)['href']

        # resp = requests.get(link, timeout=10)
        # resp.raise_for_status()  # <- no-op if status==200

        desc = listing.find('p', {'class': 'post-desc'}
                            )
        if price is not None:
            desc = desc.string

        # housing = listing.find('span', {'class': 'housing'})
        # if housing is not None:
        #     beds = housing.decode_contents().split('br')[0][-1]
        #     rm = housing.decode_contents().split('m<sup>2</sup>')[0]
        #     sqm = [int(s) for s in rm.split() if s.isdigit()]
        #     if len(sqm) == 0:
        #         sqm = None
        #     else:
        #         sqm = int(sqm[0])

        this_listing = {
            # 'location': location,
            # 'link': link_href,                    # add this too
            # 'description': descr,            # and this
            'price': price,
            'description': desc,

            # 'meters': sqm,
            # 'beds': beds
        }
        extracted.append(this_listing)
    return extracted


def extract_listings_pap(parsed):
    # location_attrs = {'data-latitude': True, 'data-longitude': True}
    listings = parsed.find_all(
        'div', {'class': "box search-results-item"})
    extracted = []

    for listing in listings[0:]:
        # hood = listing.find('span', {'class': 'result-hood'})
        # # print(hood)
        # # location = {key: listing.attrs.get(key, '') for key in location_attrs}
        # link = listing.find('a', {'class': 'result-title hdrlnk'})  # add this
        # if link is not None:
        #     descr = link.string.strip()
        #     link_href = link.attrs['href']

        price = listing.find('span', {'class': 'price'})
        if price is not None:
            price = float(price.string.split()[0].replace('.', ''))

        ref = listing.find('div', {'class': 'float-right'}).find('a', href=True)['href']
        base = 'http://www.pap.fr/' + ref
        resp = requests.get(base, timeout=10)
        resp.raise_for_status()  # <- no-op if status==200
        resp_comb = parse_source(resp.content, resp.encoding)
        pieces =resp_comb.find_all('ul', {'class': 'item-summary'})[0].find_all('strong')[0]
        chambre =resp_comb.find_all('ul', {'class': 'item-summary'})[0].find_all('strong')[1]
        print(resp_comb.find_all('ul', {'class': 'item-summary'})[0].find_all('strong')[2].string.string)
        meters = resp_comb.find_all('ul', {'class': 'item-summary'})[0].find_all('strong').string.split()[0]

        # link = listing.find('div', {'class': 'listos'}).find('a',href=True)['href']

        # resp = requests.get(link, timeout=10)
        # resp.raise_for_status()  # <- no-op if status==200

        # desc = listing.find('p', {'class': 'post-desc'}
        #                     )
        # if price is not None:
        #     desc = desc.string

        # housing = listing.find('span', {'class': 'housing'})
        # if housing is not None:
        #     beds = housing.decode_contents().split('br')[0][-1]
        #     rm = housing.decode_contents().split('m<sup>2</sup>')[0]
        #     sqm = [int(s) for s in rm.split() if s.isdigit()]
        #     if len(sqm) == 0:
        #         sqm = None
        #     else:
        #         sqm = int(sqm[0])

        this_listing = {
            # 'location': location,
            # 'link': link_href,                    # add this too
            # 'description': descr,            # and this
            'price': price,
            # 'description': desc,

            # 'meters': sqm,
            # 'beds': beds
        }
        extracted.append(this_listing)
    return extracted

# parsed.find_all(
#     ...:         'div', {'class': "box search-results-item"})[0].find('div',{'class':'float-right'}).find('a',href=True)['href']


def extract_listings(parsed):
    # location_attrs = {'data-latitude': True, 'data-longitude': True}
    listings = parsed.find_all("li", {"class": "result-row"})
    extracted = []

    for listing in listings[2:]:
        hood = listing.find('span', {'class': 'result-hood'})
        # print(hood)
        # location = {key: listing.attrs.get(key, '') for key in location_attrs}
        link = listing.find('a', {'class': 'result-title hdrlnk'})  # add this
        if link is not None:
            descr = link.string.strip()
            link_href = link.attrs['href']

        price = listing.find('span', {'class': 'result-price'})
        if price is not None:
            if price.string is not None:
                price = int(price.string[1:])

        housing = listing.find('span', {'class': 'housing'})
        if housing is not None:
            beds = housing.decode_contents().split('br')[0][-1]
            rm = housing.decode_contents().split('m<sup>2</sup>')[0]
            sqm = [int(s) for s in rm.split() if s.isdigit()]
            if len(sqm) == 0:
                sqm = None
            else:
                sqm = int(sqm[0])

        this_listing = {
            # 'location': location,
            'link': link_href,                    # add this too
            'description': descr,            # and this
            'price': price,
            'meters': sqm,
            'beds': beds
        }
        extracted.append(this_listing)
    return extracted


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = read_search_results()
    else:
        html, encoding = fetch_search_results(
            minAsk=500, maxAsk=1400, bedrooms=1
        )
    doc = parse_source(html, encoding)
    print(doc.prettify(encoding=encoding))
