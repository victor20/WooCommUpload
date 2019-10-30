from WooCommUpload.Upload.dynamo_handler import *
from WooCommUpload.Upload.s3_handler import *
from WooCommUpload.Upload.rest_handler_rec import *
from WooCommUpload.Margin.margin_extract import *
import math

dynamoHandler = DynamoHandler()
s3Handler = S3Handler()

restApiHandlerRec = RestApiHandlerRec()
marginExtract = MarginExtract()

# 0.40
MARGIN_LIMIT = 0.40
# 0.75
DISCOUNT = 0.75

def main():
    upload_products(None)
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
        change_product_name(product)
        change_description(product)
        add_product_out_price(product)
        add_discount(product)
        # add_product_img_ref(product)

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
    restApiHandlerRec.upload(products)
    
def change_product_name(product):
    if int(product.min_quantity) > 1:
        name = product.product_name
        min_quantity = product.min_quantity

        text_to_append = " (" + min_quantity + " st)"
        product.product_name = name + text_to_append

def change_description(product):
    if int(product.min_quantity) > 1:
        description = product.product_description
        min_quantity = product.min_quantity

        text_to_append = "<p><b>OBS, förpackning " + min_quantity + " st.</b></p>"
        product.product_description = description + text_to_append

def add_product_img_ref(product):
    product.product_images = s3Handler.get_images(product.supplier_product_id)

def add_product_out_price(product):
    #markup = marginExtract.get_markup(product.categories)
    margin = marginExtract.get_margin(product.categories)
    in_price = product.product_in_price

    if margin == None:
        margin = MARGIN_LIMIT

    if margin < MARGIN_LIMIT:
        margin = MARGIN_LIMIT

    out_price = in_price/(1-margin)

    print(product.supplier_product_id)
    print("    Product in price: " + str(in_price))
    #print("    Type: " + str(type(in_price)))

    print("    Margin: " + str(margin))
    #print("    Type: " + str(type(margin)))

    print("    Product out price not rounded: " + "{0:.2f}".format(out_price))
    #print("    Type: " + str(type(out_price)))

    # >= 1000
    if out_price >= 1000:
        out_price = math.ceil(out_price / 10.0) * 10.0
    elif out_price >= 10:
        out_price = math.ceil(out_price / 1.0) * 1.0
    #else:
    #    out_price = math.ceil(out_price * 10.0) / 1.00

    print("    Product out price rounded: " + "{0:.2f}".format(out_price))
    #print("    Type: " + str(type(out_price)))

    product.product_out_price = "{0:.2f}".format(out_price)


def add_discount(product):
    discount_price = float(product.product_out_price) * DISCOUNT
    product.product_discount_price = "{0:.2f}".format(discount_price)
    print("    Product discount price: " + product.product_discount_price)
    print("")

def upload_product_by_id(supplier_product_id):
    products = dynamoHandler.get_product_by_id(supplier_product_id)
    for product in products:
        product.print_product()
    restApiHandlerRec.upload(products)

def update_category_display():
    restApiHandlerRec.update_category_display()

def delete_products():
    restApiHandlerRec.delete_all_products()
    restApiHandlerRec.delete_all_categories()
    #wooApiHandler.force_delete_all_products()





main()