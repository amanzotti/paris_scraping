import requests
from bs4 import BeautifulSoup
import sys
import numpy as np
# then add this function lower down
from memory_profiler import profile
import pandas as pd
from sortedcontainers import SortedDict
import datetime


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_pap():
    base = 'http://www.pap.fr/annonce/locations-appartement-paris-14e-g37781'
    resp = requests.get(base, timeout=15)
    resp.raise_for_status()  # <- no-op if status==200
    resp_comb = resp.content
    listing = []
    string = {}
    string[15] = '15e-g37782'
    string[13] = '13e-g37780'
    string[14] = '14e-g37781'

    for i in [13, 14, 15]:
        print(i)
        base2 = 'http://www.pap.fr/annonce/locations-appartement-paris-{}'.format(string[i])
        try:
            resp_ = requests.get(base2, timeout=15)
        except:
            break
        # resp_.raise_for_status()  # <- no-op if status==200
        if resp_.status_code == 404:
            break
        parsed = parse_source(resp_.content, resp_.encoding)
        listing.append(extract_listings_pap(parsed))
        # print(listing)

        # resp_comb += resp_.content + resp_comb

        for j in np.arange(1, 7):
            print(j)
            base2 = 'http://www.pap.fr/annonce/locations-appartement-paris-{}-{}'.format(
                string[i], j)
            try:

                resp_ = requests.get(base2, timeout=10)
            except:
                break
            # resp_.raise_for_status()  # <- no-op if status==200
            if resp_.status_code == 404:
                break
            # resp_comb += resp_.content + resp_comb
            parsed = parse_source(resp_.content, resp_.encoding)
            listing.append(extract_listings_pap(parsed))

    # return resp_comb, resp.encoding
    return listing


def fetch_fusac():
    base = 'http://ads.fusac.fr/ad-category/housing/'
    listing = []
    resp = requests.get(base, timeout=10)
    resp.raise_for_status()  # <- no-op if status==200
    resp_comb = resp.content
    parsed = parse_source(resp.content, resp.encoding)
    listing.append(extract_listings_fusac(parsed))

    for i in np.arange(0, 6):
        print(i)
        base2 = 'http://ads.fusac.fr/ad-category/housing/page/{}/'.format(i)
        resp_ = requests.get(base2, timeout=10)
        # resp_.raise_for_status()  # <- no-op if status==200
        if resp_.status_code == 404:
            break
        resp_comb += resp_.content + resp_comb
        parsed = parse_source(resp_.content, resp_.encoding)
        listing.append(extract_listings_fusac(parsed))
    # return resp_comb, resp.encoding
    return listing
# handle response 200


def fetch_search_results(
    query=None, minAsk=600, maxAsk=1450, bedrooms=None, bundleDuplicates=1,
    pets_cat=1
):

    listing = []
    search_params = {
        key: val for key, val in locals().items() if val is not None
    }
    if not search_params:
        raise ValueError("No valid keywords")

    base = 'https://paris.craigslist.fr/search/apa'
    resp_ = requests.get(base, params=search_params, timeout=3)
    resp_.raise_for_status()  # <- no-op if status==200
    parsed = parse_source(resp_.content, resp_.encoding)
    listing.append(extract_listings(parsed))
    return listing


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
            'price': price,
            'desc': desc,


            # ====

            # 'description': descr,
            'pieces': None,
            'meters': None,
            'chambre': None,
            'ars': None,
            'link': None
        }
        extracted.append(SortedDict(this_listing))
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
        descr = resp_comb.find_all('p', {'class': 'item-description'})[0]
        try:
            ars = int(resp_comb.find(
                'div', {'class': 'item-geoloc'}).find('h2').string.split('e')[0][-2:])
        except:
            break
            pieces = None
            chambre = None
            square_meters = None

        try:
            pieces = int(resp_comb.find_all(
                'ul', {'class': 'item-summary'})[0].find_all('strong')[0].string)
        except:
            pieces = None
        try:
            chambre = int(resp_comb.find_all(
                'ul', {'class': 'item-summary'})[0].find_all('strong')[1].string)
        except:
            chambre = None
        try:
            square_meters = int(resp_comb.find_all(
                'ul', {'class': 'item-summary'})[0].find_all('strong')[2].string.split()[0])
        except:
            square_meters = None

        # meters = resp_comb.find_all('ul', {'class': 'item-summary'}
        #                             )[0].find_all('strong').string.split()[0]

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
            'desc': None,
            'pieces': pieces,
            'meters': square_meters,
            'chambre': chambre,
            'ars': ars,
            # 'meters': sqm,
            # 'beds': beds
            'link': None
        }
        extracted.append(SortedDict(this_listing))
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
            'desc': descr,            # and this
            'price': price,
            'meters': sqm,
            'chambre': beds,
            'pieces': None,
            'ars': None
        }
        extracted.append(SortedDict(this_listing))
    return extracted


if __name__ == '__main__':
    # df = pd.read_pickle('./ipapartment_paris.pk')
    df = pd.DataFrame
    resu = []
    print('loading fusac')
    resu.append(fetch_fusac())
    print('loading pap')
    resu.append(fetch_pap())
    print('loading craig')
    resu.append(fetch_search_results())
    flat = [item for lis in resu for lis1 in lis for item in lis1]
    df_new = pd.DataFrame(flat)
    print('saving..')
    # df_new.to_pickle('./apartment_paris_{}.pk'.format(str(datetime.datetime.now())))
    # df = pd.concat([df, df_new])
    df_new.to_pickle('./apartment_paris.pk')
    print('Done.')
