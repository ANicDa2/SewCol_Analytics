import json
import csv
import os
import requests
import argparse
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

CLIENT_ID = os.getenv('EBAY_CLIENT_ID')
CLIENT_SECRET = os.getenv('EBAY_CLIENT_SECRET')
ACCESS_TOKEN_URL = os.getenv('EBAY_ACCESS_TOKEN_URL')
SCOPE = os.getenv('EBAY_SCOPE')
HOST = 'https://api.ebay.com/buy/browse/v1'

def get_auth_token():
 
    response = requests.post(ACCESS_TOKEN_URL, data={
        'grant_type': 'client_credentials',
        'scope': SCOPE
    }, auth=(CLIENT_ID, CLIENT_SECRET))

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Failed to obtain token: {response.status_code} {response.text}")

BEARER_TOKEN = get_auth_token()

def fetch_item_details(item_href):
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}','X-EBAY-C-MARKETPLACE-ID':'EBAY_AU'}
    response = requests.get(item_href, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'No Item Summaries for {item_href}')
        return {}
    

def fetch_item_summary(category, brand, limit):
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}','X-EBAY-C-MARKETPLACE-ID':'EBAY_AU'}
    all_items = []
    offset = 0

    while True:
        url = f"{HOST}/item_summary/search?q={brand}&limit={limit}&offset={offset}&aspect_filter=categoryId:{category},Brand:{{{brand}}}&category_ids={category}"
        print(url)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            item_summaries = data.get('itemSummaries', [])
            all_items.extend(item_summaries)
            total = data.get('total', 0)
            offset += limit
            if offset >= total:
                break
        else:
            print(f'No Item Summaries. Response Status Code: {response.status_code}')
            break

    return all_items

def extract_to_csv(item_summaries, csv_file):

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'ShortDescription', 'Condition', 'SellerItemRevision', 'ItemId', 'Price', 'Currency', 'Color', 'Size', 'Material', 'Brand', 'SellerUsername', 'ItemWebUrl', 'ItemCreationDate', 'ItemHref', 'ImageURL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for item in tqdm(item_summaries, desc="Processing items"):
            item_details = fetch_item_details(item.get('itemHref', ''))
            item_creation_date_str = item.get('itemCreationDate', '')
            item_creation_date = datetime.strptime(item_creation_date_str, '%Y-%m-%dT%H:%M:%S.%fZ') if item_creation_date_str else None
            writer.writerow({
                'Title': item.get('title', ''),
                'ShortDescription': item_details.get('shortDescription', ''),
                'Condition': item.get('condition', ''),
                'SellerItemRevision': item_details.get('sellerItemRevision', ''),
                'ItemId': item_details.get('itemId', ''),
                'Price': item.get('price', {}).get('value', ''),
                'Currency': item.get('price', {}).get('currency', ''),
                'Color': item_details.get('color', ''),
                'Size': item_details.get('size', ''),
                'Material': item_details.get('material', ''),
                'Brand': brand,
                'SellerUsername': item_details.get('seller', {}).get('username', ''),
                'ItemWebUrl': item.get('itemWebUrl', ''),
                'ItemCreationDate': item_creation_date,
                'ItemHref': item.get('itemHref', ''),
                'ImageURL': item.get('image', {}).get('imageUrl', ''),
            })

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Search eBay for items of a specific brand.')
    parser.add_argument('--brand', type=str, help='The brand to search for on eBay.')
    args = parser.parse_args()

    brand = args.brand
    if not brand:
        brand = input("Please enter the brand to search for: ")

    category = '63861'
    limit = '200'

    item_summaries = fetch_item_summary(category, brand, limit)

    if item_summaries:
        extract_to_csv(item_summaries, f'data\{brand}.csv')
    else:
        print("No item summaries found. CSV extraction skipped.")
