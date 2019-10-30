import boto3
import json
from WooCommUpload.Upload.Model.product import *
from WooCommUpload.Config import cred

class DynamoHandler:

    def __init__(self):
        dynamo_db = boto3.resource(
            'dynamodb',
            aws_access_key_id=cred.aws_access_key_id,
            aws_secret_access_key=cred.aws_secret_access_key,
            region_name=cred.region_name)

        self.emo_products = dynamo_db.Table(cred.table_name)
        self.c_products = dynamo_db.Table(cred.table_name)


    def get_product_by_id(self, supplier_product_id):
        products = []
        key = {}
        key['supplierProductId'] = supplier_product_id
        response = self.emo_products.get_item(Key=key)
        item = response['Item']
        products.append(self.create_product(item))

        return products

    def get_products(self, qty = None):
        print("")
        products = []

        response = self.emo_products.scan()
        dynamo_items = response['Items']
        count = 0
        while True:
            for dynamo_item in dynamo_items:
                if qty is None or count < qty:
                    products.append(self.create_product(dynamo_item))
                    count += 1

            print(str(count) + " DYNAMO PRODUCTS DOWNLOADED")
            if qty is None or count < qty:
                if 'LastEvaluatedKey' in response:
                    response = self.emo_products.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    dynamo_items = response['Items']
                else:
                    break
            else:
                break

        return products

    def create_product(self, dynamo_item):
        product = Product(
            supplier_product_id = dynamo_item['supplierProductId'],
            product_name = dynamo_item['productName'])

        product.categories = self.trim_categories(dynamo_item['categories'])

        if "minQuantity" in dynamo_item.keys():
            product.min_quantity = dynamo_item['minQuantity']

        product_in_price = dynamo_item['productPrice']
        product_in_price = product_in_price.replace(",", "." )
        product.product_in_price = float(product_in_price)

        description = self.get_description(dynamo_item)
        if description:
            product.product_description = description

        attributes = self.get_specifications(dynamo_item)
        if attributes:
            product.product_specification = attributes

        return product

    def trim_categories(self, categories):
        categories = [item.strip() for item in categories]
        categories = [item.replace("  ", " ") for item in categories]
        return categories

    def get_description(self, dynamo_item):
        subheader = ""
        group_description = ""
        item_description = ""

        if dynamo_item['productText']['subheader']:
            subheader = "<p><b>" + dynamo_item['productText']['subheader'] + "</b></p>"

        if dynamo_item['productText']['groupDescription']:
            group_description = "<p>" + dynamo_item['productText']['groupDescription'] + "</p>"

        if dynamo_item['productText']['itemDescription']:
            item_description = dynamo_item['productText']['itemDescription']

        description = subheader + group_description + item_description

        return description

    def get_specifications(self, product):
        # 1. Vikt
        # 2. Volym

        attributes = []
        weight = product['productSpecification'][0]['value']
        volume = product['productSpecification'][1]['value']
        attributes.append({"name": "Vikt", "visible": True, "options": [weight]})
        attributes.append({"name": "Volym", "visible": True, "options": [volume]})

        return attributes

