from bs4 import BeautifulSoup
import requests
import json
import re


url = 'https://www.walmart.com/ip/SAMSUNG-27-Class-Curved-1920x1080-VGA-HDMI-60hz-4ms-AMD-FREESYNC-HD-LED-Monitor-LC27F396FHNXZA/117633165?athbdg=L1102&from=/search'

headers = {
    'Accept' : '*/*',
    'Accept-Encoding' : 'gzip, deflate, br, zstd',
    'Accept-Language' : 'en-US,en;q=0.9,pt;q=0.8,es;q=0.7',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def get_product_links(query, page_number=1):
    search_url = f'https://www.walmart.com/search?q={query}&page={page_number}'

    r = requests.get(search_url, headers=headers)

    soup = BeautifulSoup(r.content, 'html.parser')
    
    product_items = soup.find_all('div', attrs={'class':'mb0 ph0-xl pt0-xl bb b--near-white w-25 pb3-m ph1'})

    product_links = []
    
    for product_item in product_items:
        base_url = 'https://www.walmart.com'
        raw_link = product_item.find('a', href=True)
        pattern = r'/ip/.*'
        link = re.search(pattern, raw_link['href'])
        if link:
            product_links.append(base_url + link.group())

    return product_links


def extract_product_info(url):
    r = requests.get(url=url, headers=headers)
    print(r.status_code)

    soup = BeautifulSoup(r.content, 'html.parser')

    data = soup.find('script', attrs={'type':'application/ld+json'}).get_text()

    data_json  = json.loads(data)

    try:
        product_info = {
            'price' : data_json['offers']['price'],
            'review' : data_json['aggregateRating']['reviewCount'],
            'sku' : data_json['sku'],
            'rating' : data_json['aggregateRating']['ratingValue'],
            'name' : data_json['name'],
            'model' : data_json['model'],
            'image_url' : data_json['image'],
            'description' : data_json['description']
        }
        return json.dumps(product_info, indent=2)
    except Exception as e:
        return json.dumps({'error':'missing information'})

def main():
    filename = 'data.json'
    for i in range(1, 10):
        print(f'Searching page {i}')
        for url in get_product_links('monitor', i):
            with open(filename, 'a') as f:
                f.write(extract_product_info(url)+'\n')


if __name__ == "__main__":
    main()