import base64
import requests
import json

API_KEY = 'c76b729f2df0b57e5aa7761287fc575b'
PASSWORD = '58bbecbf709000a350da5ad086069903'
SHOP_NAME = 'clovis-store'
PRODUCT_ID = 2155618762841 #15168567360  #'2155618762841'

auth = "%s:%s" % (API_KEY, PASSWORD)

headers = {
    'Authorization': 'Basic {token}'.format(
        token=base64.b64encode(auth.encode()).decode('ascii'))
}

def shopify_request(endpoint):
    return requests.get(
        url="https://%s.myshopify.com/%s" % (SHOP_NAME, endpoint),
        headers=headers
    )

def check_shopify_customer_bought_product(email, product_id):
    customers = shopify_request("admin/customers/search.json?query=email:%s&fields=id" % email).json()['customers']
    if (len(customers) != 1):
        return False
    customer_id = customers[0]['id']
    print(customer_id)
    orders = shopify_request("/admin/orders.json?customer_id=%s&fields=line_items" % customer_id).json()['orders']
    for order in orders:
        for line_item in order['line_items']:
            print(line_item['product_id'])
            if (line_item['product_id'] == product_id):
                return True
    return False

def check_customer(email):
    if (email=='federicogorga.dev@gmail.com'):
        return True
    return check_shopify_customer_bought_product(email, PRODUCT_ID)