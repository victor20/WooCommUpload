"""
Settings for wp-config.php
@ini_set ( 'max_input_vars' , 2000 );
set_time_limit( 600 );
define( 'WP_MEMORY_LIMIT', '256M' ); 

"""

from woocommerce import API
import json
import html
from WooCommUpload.Upload.Model.remote_product import *
from WooCommUpload.Upload.Model.category import *
from WooCommUpload.Config import cred

class WooApiHandler:

    def __init__(self):
        self.wcapi = API(
            # WC Office
            url=cred.url,
            consumer_key=cred.consumer_key,
            consumer_secret=cred.consumer_secret,
            version=cred.version,
            timeout=cred.timeout)

        self.products_uploaded = 0

    def get_sub_categories(self, parent_id):
        """CHANGE WOO PAGE"""

        params = {"per_page": "100", "parent": parent_id}
        get_sub_categories_response = self.wcapi.get("products/categories", params=params).json()

        remote_sub_categories = []
        count = 0
        for item in get_sub_categories_response:
            remote_sub_categories.append(self.create_remote_category(item))
            count += 1

        return remote_sub_categories

    def create_remote_category(self, item):
        #print(json.dumps(item, indent=4, sort_keys=True))
        category = Category(html.unescape(item['name']), item['id'])
        category.parent_remote_id = item['parent']
        #category.print_category(1)

        return category

    def get_products(self):
        remote_products = []
        count = 0
        page = 1
        while True:
            params = {
                "per_page": "100",
                "page": page
            }
            get_products_response = self.wcapi.get("products", params=params).json()
            for woo_product_item in get_products_response:
                remote_products.append(self.create_remote_product(woo_product_item))
                count += 1
            page += 1
            print("DOWLOADED " + str(count) + " PRODUCTS")
            if len(get_products_response) < 100:
                break

        print(str(count) + " TOTAL PRODUCTS ALREADY ON SITE")
        return remote_products

    def create_remote_product(self, woo_product_item):
        categories = []
        for category in woo_product_item['categories']:
            categories.append(category['id'])
        remote_category_id = categories[0]

        remote_image_ids = []
        for remote_image in woo_product_item['images']:
            remote_image_ids.append(remote_image['id'])

        remoteProduct = RemoteProduct(
            supplier_product_id = woo_product_item['sku'],
            remote_product_id = woo_product_item['id'],
            remote_category_id = remote_category_id,
            product_name = html.unescape(woo_product_item['name']),
            remote_image_ids = remote_image_ids)

        return remoteProduct

    def add_category(self, name, pId):
        data = {"name": name, "display": "both", "parent": pId}
        response = self.wcapi.post("products/categories", data).json()
        # print(json.dumps(response, indent=4, sort_keys=True))

        if "id" in response.keys():
            print("    Uploaded: " + name + " ---> " + str(response['id']))
            return response['id']
        else:
            print("Not Uploaded")
            return ""

    def upload_products(self, products):
        """
        When batch upload fails try to upload single products
        Raise batch size to 100
        """

        self.print_title("uploading products")

        uploaded_products = []

        while products:
            product_batch = []
            for i in range(30):
                if products:
                    product_batch.append(products.pop())
                else:
                    break

            data = {}
            create = []
            for product in product_batch:
                if not product.supplier_product_id == "148902":
                    create.append(self.create_woo_product(product))

            data['create'] = create

            try:
                batch_upload_response = self.wcapi.post("products/batch", data).json()

                if "create" in batch_upload_response.keys():
                    uploaded_products.extend(self.create_remote_products(batch_upload_response))
                else:
                    print(json.dumps(batch_upload_response, indent=4, sort_keys=True))
            except:
                print("An exception occurred")

        return uploaded_products

    def create_remote_products(self, batch_upload_response):

        #print(json.dumps(batch_upload_response, indent=4, sort_keys=True))
        #print(batch_upload_response['create'])

        uploaded_products = []
        woo_products = batch_upload_response['create']

        for woo_product in woo_products:
            uploaded_products.append(self.create_remote_product(woo_product))
            self.products_uploaded += 1

        #for uploaded_product in uploaded_products:
        #    uploaded_product.print_remote_product()

        print(str(self.products_uploaded) + " TOTAL PRODUCTS UPLOADED")

        return  uploaded_products

    def create_woo_product(self, product):
        woo_product = {}

        cat_id = product.remote_category_id
        # print(catId)

        woo_product['sku'] = product.supplier_product_id
        woo_product['categories'] = [{"id": cat_id}]
        woo_product['name'] = product.product_name
        woo_product['type'] = "simple"
        woo_product['regular_price'] = product.product_out_price

        woo_product['description'] = product.product_description
        woo_product['short_description'] = product.product_description
        woo_product['attributes'] = product.product_specification
        woo_product['images'] = product.product_images

        return woo_product

    def update_category_image(self, category, img_ref):
        data = {
            "image": {"id": img_ref}
        }

        request = "products/categories/" + str(category.remote_id)
        update_category_image_response = self.wcapi.put(request, data).json()

        #print(json.dumps(update_category_image_response, indent=4, sort_keys=True))


    def force_delete_all_products(self):
        params = {"per_page": "100"}
        response_get = self.wcapi.get("products", params=params).json()

        products_to_delete = [d['id'] for d in response_get]
        params = {"force": "True"}

        for p in products_to_delete:
            print(p)
            response_delete = self.wcapi.delete("products/" + str(p), params=params).json()

    def delete_all_products(self):
        count = 0
        while True:
            params = {"per_page": "100"}
            response_get = self.wcapi.get("products", params=params).json()

            products_to_delete = [d['id'] for d in response_get]
            data = {'delete': products_to_delete}
            response_delete = self.wcapi.post("products/batch", data).json()
            count += len(products_to_delete)
            if len(products_to_delete) < 100:
                break
            else:
                print("Deleted products: " + str(count))

        print("")
        print("Deleted products: " + str(count))

    def delete_all_categories(self):

        count = 0
        while True:
            params = {"per_page": "100"}
            response_get = self.wcapi.get("products/categories", params=params).json()

            categories_to_delete = [d['id'] for d in response_get]
            data = {'delete': categories_to_delete}
            response_delete = self.wcapi.post("products/categories/batch", data).json()
            count += len(categories_to_delete)
            if len(categories_to_delete) < 100:
                break
            else:
                print("Deleted categories: " + str(count))

        print("")
        print("Deleted categories: " + str(count))

    def print_title(self, title):
        print("")
        print("----------")
        print("")
        print(title.upper() + ":")
        print("")
