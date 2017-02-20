import requests
from bs4 import BeautifulSoup
import sys

# then add this function lower down


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def fetch_fusac():
    base = 'http://ads.fusac.fr/ad-category/housing/'
    resp = requests.get(base, timeout=3)
    resp.raise_for_status()  # <- no-op if status==200
    return resp.content, resp.encoding

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

    for listing in listings[2:]:
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
            # 'meters': sqm,
            # 'beds': beds
        }
        extracted.append(this_listing)
    return extracted


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
    print doc.prettify(encoding=encoding)