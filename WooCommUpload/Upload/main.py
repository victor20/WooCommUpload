from WooCommUpload.Upload.dynamo_handler import *
from WooCommUpload.Upload.s3_handler import *
from WooCommUpload.Upload.rest_handler_rec import *
from WooCommUpload.Margin.margin_extract import *

dynamoHandler = DynamoHandler()
s3Handler = S3Handler()

restApiHandlerRec = RestApiHandlerRec()
marginExtract = MarginExtract()

MARGIN = 1.20

MARGIN_LIMIT = 1.10
MARGIN_LIMIT_FOR_DISCOUNT = 1.15
DISCOUNT = 0.90

def main():
    upload_products(10)
    #delete_products()
    #update_category_display()

def upload_products(qty):

    products = dynamoHandler.get_products(qty)

    count = 0
    count_products_with_img = 0
    count_products_without_img = 0
    last_count = 0

    print("")
    print("Adding prices and downloading images")
    print("")

    for product in products:
        #add_product_img_ref(product)
        #add_product_out_price(product)
        #add_discount(product)
        #product.print_product()

        if product.product_images:
            count_products_with_img += 1
        else:
            count_products_without_img += 1

        count += 1
        if count - last_count > 299:
            print(str(count) + " PRODUCTS PRICED |" +
                               " WITH IMG: " + str(count_products_with_img) +
                               " - WITHOUT IMG: " + str(count_products_without_img))
            last_count = count

    print("")
    print(str(count) + " PRODUCTS PRICED |" +
          " WITH IMG: " + str(count_products_with_img) +
          " - WITHOUT IMG: " + str(count_products_without_img))
    print("")
    #restApiHandlerRec.upload_products(products)
    


def add_product_img_ref(product):
    product.product_images = s3Handler.get_images(product.supplier_product_id)

def add_product_out_price(product):
    margin = marginExtract.get_margin(product.categories)

    """
    print("Type of product price")
    print(type(product.product_in_price))
    print("Margin")
    print(margin)
    print("")
    """

    print(product.supplier_product_id)

    if margin == None:
        margin = 1.20

    elif margin < MARGIN_LIMIT:
        margin = MARGIN_LIMIT

    product_out_price = product.product_in_price * margin
    product_out_price = "{0:.2f}".format(product_out_price)
    print("In Price: " + str(product.product_in_price))
    print("Out Price: " + str(product_out_price))
    print("Margin no discount (%): " + "{0:.2f}".format(margin))
    product.product_out_price = str(product_out_price)


def add_discount(product):
    margin = float(product.product_out_price)/product.product_in_price

    if margin < MARGIN_LIMIT_FOR_DISCOUNT:
        discount = 0.00
    else:
        discount = DISCOUNT


    product_discount_price = float(product.product_out_price) * discount
    product_discount_price = "{0:.2f}".format(product_discount_price)
    print("Discount price: " + str(product_discount_price))
    margin_c = float(product.product_out_price) - float(product.product_out_price) * discount
    print("Margin (kr) with discount: " + "{0:.2f}".format(margin_c))
    margin_p = float(product.product_out_price) * discount/product.product_in_price
    print("Margin (%) with discount: " + "{0:.2f}".format(margin_p))
    product.product_discount_price = str(product_discount_price)
    print("")

def upload_product_by_id(supplier_product_id):
    products = dynamoHandler.get_product_by_id(supplier_product_id)
    for product in products:
        product.print_product()
    restApiHandlerRec.upload_products(products)

def update_category_display():
    restApiHandlerRec.update_category_display()

def delete_products():
    restApiHandlerRec.delete_all_products()
    restApiHandlerRec.delete_all_categories()
    #wooApiHandler.force_delete_all_products()





main()