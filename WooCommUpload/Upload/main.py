from WooCommUpload.Upload.dynamo_handler import *
from WooCommUpload.Upload.s3_handler import *
from WooCommUpload.Upload.rest_handler_rec import *

dynamoHandler = DynamoHandler()
s3Handler = S3Handler()

restApiHandlerRec = RestApiHandlerRec()

MARGIN = 1.20

def main():
    upload_products(5)
    #delete_products()

def upload_products(qty):
    products = dynamoHandler.get_products(qty)
    count = 0
    for product in products:
        add_product_img_ref(product)
        add_product_out_price(product)
        #product.print_product()
        count += 1

    print("")
    print(str(count) + " PRODUCTS CREATED BY DYNAMO HANDLER")
    print("")
    restApiHandlerRec.upload_products(products)

def add_product_img_ref(product):
    product.product_images = s3Handler.get_images(product.supplier_product_id)

def add_product_out_price(product):
    product.product_out_price = product.product_in_price * MARGIN

def upload_product_by_id(supplier_product_id):
    products = dynamoHandler.get_product_by_id(supplier_product_id)
    for product in products:
        product.print_product()
    restApiHandlerRec.upload_products(products)

def delete_products():
    restApiHandlerRec.delete_all_products()
    restApiHandlerRec.delete_all_categories()
    #wooApiHandler.force_delete_all_products()





main()