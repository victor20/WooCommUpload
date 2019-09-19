from WooCommUpload.Upload.Model.category import *
from WooCommUpload.Upload.Model.remote_product import *
from WooCommUpload.Upload.woo_api_handler import *
import time

class RestApiHandlerRec:

    def __init__(self):
        self.wooApiHandler = WooApiHandler()
        self.root_category = Category("root", 0)
        self.products_to_be_uploaded = []

        self.remote_products_count = 0
        self.categories_uploaded_count = 0

    def upload_products(self, products):
        self.add_remote_categories()
        self.add_remote_products()

        self.add_local_products(products)
        self.upload_products_to_be_uploaded(self.products_to_be_uploaded)

        self.add_category_images()

    def add_remote_categories(self):
        print("Adding remote categories")

        self.add_remote_categories2(self.root_category)
        #self.print_tree()

        print("")
        print(str(self.remote_products_count) + " REMOTE CATEGORIES")
        print("")

    def add_remote_categories2(self, current_category):

        """
        Denna verkar inte fungera korrekt. När du laddar upp kategorier igen
        försöker den ladda upp redan existerande kategorier
        """

        sub_categories = self.wooApiHandler.get_sub_categories(current_category.remote_id)
        if len(sub_categories) > 0:
            current_category.sub_categories = sub_categories
            for sub_category in sub_categories:
                self.remote_products_count += 1
                self.add_remote_categories2(sub_category)

    def add_remote_products(self):

        remote_products = self.wooApiHandler.get_products()

        for remote_product in remote_products:
            #remote_product.print_remote_product()

            start = time.time()
            self.add_remote_product(remote_product, self.root_category)
            end = time.time()
            #print("        Time: " + str(end - start))

        self.print_tree()

    def add_remote_product(self, remote_product, current_category):

        for subcat in current_category.sub_categories:
            if subcat.remote_id == remote_product.remote_category_id:
                subcat.products.append(remote_product)
                return

        for subcat in current_category.sub_categories:
            self.add_remote_product(remote_product, subcat)

    def add_local_products(self, products):

        print("Adding categories")

        for product in products:
            self.add_local_product(product, 0, self.root_category)
        #self.print_tree()

        print("")
        print(str(self.categories_uploaded_count) + " CATEGORIES UPLOADED")
        print("")

    def add_local_product(self, product, level, current_category):

        if level == len(product.categories):

            """
            if product.remote_product_id:
                current_category.products.append(product)
            """

            match = False
            for remote_product in current_category.products:
                if product.supplier_product_id == remote_product.supplier_product_id:
                    match = True

            if not match:
                product.remote_category_id = current_category.remote_id
                self.products_to_be_uploaded.append(product)

        else:
            match = False
            for subcat in current_category.sub_categories:
                if subcat.name == product.categories[level]:
                    self.add_local_product(product, level + 1, subcat)
                    match = True

            if not match:
                category_name = product.categories[level]
                print("")
                print("Adding " + str(category_name))
                remote_id = self.wooApiHandler.add_category(category_name, current_category.remote_id)

                if remote_id:
                    category = Category(category_name, remote_id)
                    current_category.sub_categories.append(category)
                    self.add_local_product(product, level + 1, category)

                    self.categories_uploaded_count += 1

    def upload_products_to_be_uploaded(self, products):
        #self.print_title("products to be uploaded")
        count = 0
        for product in products:
            #product.print_product()
            count += 1

        print("PRODUCTS TO BE UPLOADED: " + str(count))

        remote_products = self.wooApiHandler.upload_products(products)

        #self.print_title("uploaded products")
        count = 0
        for product in remote_products:
            #product.print_product()
            count += 1

        print("PRODUCTS UPLOADED: " + str(count))

        for remote_product in remote_products:
            self.add_remote_product(remote_product, self.root_category)

        self.print_tree()

    def add_category_images(self):
        self.add_category_images2(self.root_category)

    def add_category_images2(self, current_category):
        sub_images = []
        current_images = []
        for subcat in current_category.sub_categories:
            sub_images.extend(self.add_category_images3(subcat))

        for product in current_category.products:
            current_images.extend(product.remote_image_ids)

        if current_images:
            self.wooApiHandler.update_category_image(current_category, current_images[0])
        else:
            if sub_images:
                self.wooApiHandler.update_category_image(current_category, sub_images[0])

        return sub_images + current_images

    def print_tree(self):
        self.print_title("current tree")
        self.print_tree2(0, self.root_category)

    def print_tree2(self, level, current_category):
        current_category.print_category_short(level)

        if level == 3:
            for product in current_category.products:
                print("                    " + product.product_name)
                #product.print_remote_product()

        for category in current_category.sub_categories:
            self.print_tree2(level + 1, category)

    def delete_all_products(self):
        self.wooApiHandler.delete_all_products()

    def delete_all_categories(self):
        self.wooApiHandler.delete_all_categories()

    def print_title(self, title):
        print("")
        print("----------")
        print("")
        print(title.upper() + ":")
        print("")



